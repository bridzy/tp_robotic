import math
import heapq


class GridPlannerAStar:
    def __init__(self, width_m=10.0, height_m=10.0, resolution=0.20,
                 robot_radius=0.20, safety_margin=0.05):
        self.width_m = width_m
        self.height_m = height_m
        self.resolution = resolution
        self.robot_radius = robot_radius
        self.safety_margin = safety_margin

        self.nx = int(math.ceil(width_m / resolution))
        self.ny = int(math.ceil(height_m / resolution))

        self.grid = [[0 for _ in range(self.ny)] for _ in range(self.nx)]

    # ------------------------------------------------------------------
    # Conversion monde <-> grille
    # ------------------------------------------------------------------
    def world_to_grid(self, x, y):
        i = int(x / self.resolution)
        j = int(y / self.resolution)
        i = max(0, min(self.nx - 1, i))
        j = max(0, min(self.ny - 1, j))
        return i, j

    def grid_to_world(self, i, j):
        x = (i + 0.5) * self.resolution
        y = (j + 0.5) * self.resolution
        return x, y

    # ------------------------------------------------------------------
    # Occupancy grid
    # ------------------------------------------------------------------
    def clear(self):
        for i in range(self.nx):
            for j in range(self.ny):
                self.grid[i][j] = 0

    def build_from_environment(self, env):
        """
        Construit la grille à partir des obstacles rectangulaires.
        Suppose que env.obstacles contient les bordures + murs internes.
        """
        self.clear()

        inflate = int(math.ceil((self.robot_radius + self.safety_margin) / self.resolution))

        for obs in env.obstacles:
            bounds = self._extract_bounds(obs)
            if bounds is None:
                continue

            xmin, ymin, xmax, ymax = bounds
            i0, j0 = self.world_to_grid(xmin, ymin)
            i1, j1 = self.world_to_grid(xmax, ymax)

            for i in range(max(0, i0 - inflate), min(self.nx, i1 + inflate + 1)):
                for j in range(max(0, j0 - inflate), min(self.ny, j1 + inflate + 1)):
                    self.grid[i][j] = 1

    def _extract_bounds(self, obs):
        """
        Adapte ici selon ton ObstacleRectangle.
        Cas gérés :
        - x, y, width, height
        - x, y, w, h
        - x_min, y_min, x_max, y_max
        """
        if all(hasattr(obs, k) for k in ("x_min", "y_min", "x_max", "y_max")):
            return obs.x_min, obs.y_min, obs.x_max, obs.y_max

        if all(hasattr(obs, k) for k in ("x", "y", "width", "height")):
            return obs.x, obs.y, obs.x + obs.width, obs.y + obs.height

        if all(hasattr(obs, k) for k in ("x", "y", "w", "h")):
            return obs.x, obs.y, obs.x + obs.w, obs.y + obs.h

        return None

    def is_free(self, cell):
        i, j = cell
        if i < 0 or i >= self.nx or j < 0 or j >= self.ny:
            return False
        return self.grid[i][j] == 0

    def nearest_free(self, cell, max_radius=8):
        if self.is_free(cell):
            return cell

        ci, cj = cell
        for r in range(1, max_radius + 1):
            for di in range(-r, r + 1):
                for dj in range(-r, r + 1):
                    if abs(di) != r and abs(dj) != r:
                        continue
                    cand = (ci + di, cj + dj)
                    if self.is_free(cand):
                        return cand
        return None

    # ------------------------------------------------------------------
    # A*
    # ------------------------------------------------------------------
    def heuristic(self, a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def neighbors(self, cell):
        i, j = cell
        moves = [
            (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
            (-1, -1, math.sqrt(2)), (-1, 1, math.sqrt(2)),
            (1, -1, math.sqrt(2)), (1, 1, math.sqrt(2)),
        ]

        result = []
        for di, dj, cost in moves:
            ni, nj = i + di, j + dj
            nxt = (ni, nj)
            if not self.is_free(nxt):
                continue

            # évite de couper un angle à travers un mur
            if di != 0 and dj != 0:
                if not self.is_free((i + di, j)) or not self.is_free((i, j + dj)):
                    continue

            result.append((nxt, cost))
        return result

    def astar(self, start_xy, goal_xy):
        start = self.nearest_free(self.world_to_grid(*start_xy))
        goal = self.nearest_free(self.world_to_grid(*goal_xy))

        if start is None or goal is None:
            return []

        open_heap = []
        heapq.heappush(open_heap, (0.0, start))

        came_from = {}
        g_score = {start: 0.0}
        f_score = {start: self.heuristic(start, goal)}

        closed = set()

        while open_heap:
            _, current = heapq.heappop(open_heap)

            if current in closed:
                continue
            closed.add(current)

            if current == goal:
                return self._reconstruct_path(came_from, current)

            for nxt, move_cost in self.neighbors(current):
                tentative_g = g_score[current] + move_cost

                if tentative_g < g_score.get(nxt, float("inf")):
                    came_from[nxt] = current
                    g_score[nxt] = tentative_g
                    f = tentative_g + self.heuristic(nxt, goal)
                    f_score[nxt] = f
                    heapq.heappush(open_heap, (f, nxt))

        return []

    def _reconstruct_path(self, came_from, current):
        cells = [current]
        while current in came_from:
            current = came_from[current]
            cells.append(current)
        cells.reverse()

        path = [self.grid_to_world(i, j) for i, j in cells]
        return self.simplify_path(path)

    # ------------------------------------------------------------------
    # Simplification du chemin
    # ------------------------------------------------------------------
    def simplify_path(self, path):
        if len(path) <= 2:
            return path[:]

        grid_path = [self.world_to_grid(x, y) for x, y in path]
        simplified = [grid_path[0]]

        anchor = grid_path[0]
        k = 1
        while k < len(grid_path):
            last_visible = k
            for t in range(k, len(grid_path)):
                if self.line_of_sight(anchor, grid_path[t]):
                    last_visible = t
                else:
                    break

            simplified.append(grid_path[last_visible])
            anchor = grid_path[last_visible]
            k = last_visible + 1

        out = [self.grid_to_world(i, j) for i, j in simplified]

        # supprimer doublons éventuels
        clean = [out[0]]
        for p in out[1:]:
            if math.hypot(p[0] - clean[-1][0], p[1] - clean[-1][1]) > 1e-6:
                clean.append(p)
        return clean

    def line_of_sight(self, a, b):
        x0, y0 = a
        x1, y1 = b

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x, y = x0, y0

        sx = 1 if x1 > x0 else -1
        sy = 1 if y1 > y0 else -1

        if dx >= dy:
            err = dx / 2.0
            while x != x1:
                if not self.is_free((x, y)):
                    return False
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2.0
            while y != y1:
                if not self.is_free((x, y)):
                    return False
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy

        return self.is_free((x1, y1))