import math
from .capteurs import Capteur


class Lidar(Capteur):
    """
    Lidar 2D : N rayons sur un FOV, renvoie distances + points d'impact.
    En plus des obstacles, il détecte aussi les limites du monde (largeur/hauteur).
    """
    def __init__(self, n_rays=31, fov=math.radians(180), max_range=4.0):
        """
        Paramètres :
            n_rays    : nombre de rayons émis
            fov       : champ de vision total (radians)
            max_range : portée maximale d'un rayon (mètres)
        """
        self.n_rays = int(n_rays)
        self.fov = float(fov)
        self.max_range = float(max_range)

    def _angles(self):
        """Génère la liste des angles relatifs des rayons, de -fov/2 à +fov/2."""
        if self.n_rays <= 1:
            return [0.0]
        start = -self.fov / 2
        step = self.fov / (self.n_rays - 1)
        return [start + i * step for i in range(self.n_rays)]

    @staticmethod
    def _ray_circle_intersection(ox, oy, dx, dy, cx, cy, r, max_range):
        """
        Intersection rayon → cercle de centre (cx, cy) et rayon r.
        Retourne t (distance le long du rayon) ou None.
        """
        fx = ox - cx
        fy = oy - cy
        b = 2.0 * (fx * dx + fy * dy)
        c = fx * fx + fy * fy - r * r
        disc = b * b - 4.0 * c      # a = 1 (dx,dy normalisé)
        if disc < 0:
            return None
        t = (-b - disc ** 0.5) * 0.5
        if 0.0 < t <= max_range:
            return t
        return None

    @staticmethod
    def _ray_aabb_intersection(ox, oy, dx, dy, xmin, xmax, ymin, ymax, max_range):
        """
        Intersection rayon avec un rectangle axis-aligned (AABB).
        Retourne t (distance) ou None.
        """
        t_min = 0.0
        t_max = float(max_range)

        # X
        if abs(dx) < 1e-9:
            if ox < xmin or ox > xmax:
                return None
        else:
            tx1 = (xmin - ox) / dx
            tx2 = (xmax - ox) / dx
            if tx1 > tx2:
                tx1, tx2 = tx2, tx1
            t_min = max(t_min, tx1)
            t_max = min(t_max, tx2)
            if t_min > t_max:
                return None

        # Y
        if abs(dy) < 1e-9:
            if oy < ymin or oy > ymax:
                return None
        else:
            ty1 = (ymin - oy) / dy
            ty2 = (ymax - oy) / dy
            if ty1 > ty2:
                ty1, ty2 = ty2, ty1
            t_min = max(t_min, ty1)
            t_max = min(t_max, ty2)
            if t_min > t_max:
                return None

        if 0.0 < t_min <= max_range:
            return t_min
        return None

    def read(self, env, robot):
        """
        Lance tous les rayons et retourne un dict :
            distances : liste des distances jusqu'au premier obstacle (mètres)
            hits      : liste des points d'impact (x, y) dans le monde
        """
        ox, oy = robot.x, robot.y
        base = robot.orientation

        # Limites du monde (rectangle centré en 0,0)
        L = float(getattr(env, "largeur", 10.0))
        H = float(getattr(env, "hauteur", 10.0))
        xmin, xmax = -L / 2, L / 2
        ymin, ymax = -H / 2, H / 2

        distances = []
        hits = []

        for a in self._angles():
            theta = base + a
            dx = math.cos(theta)
            dy = math.sin(theta)

            dmin = self.max_range

            # 1) obstacles
            for obs in getattr(env, "obstacles", []):
                if hasattr(obs, "intersection"):
                    t = obs.intersection(ox, oy, dx, dy, self.max_range)
                    if t is not None and 0.0 < t < dmin:
                        dmin = t

            # 2) limites du monde (AABB)
            t_world = self._ray_aabb_intersection(
                ox, oy, dx, dy, xmin, xmax, ymin, ymax, self.max_range
            )
            if t_world is not None and 0.0 < t_world < dmin:
                dmin = t_world

            # 3) Autres robots (cercles) — rendus visibles au Lidar
            for (rx, ry, rr) in getattr(env, "autres_robots", []):
                t = self._ray_circle_intersection(ox, oy, dx, dy, rx, ry, rr, self.max_range)
                if t is not None and t < dmin:
                    dmin = t

            distances.append(dmin)
            hits.append((ox + dmin * dx, oy + dmin * dy))

        return {"distances": distances, "hits": hits}

    def draw(self, vue, robot, data):
        """Trace les rayons Lidar sur l'écran (gris clair)."""
        import pygame
        hits = data.get("hits", [])
        ox, oy = vue.convertir_coordonnees(robot.x, robot.y)
        for (hx_m, hy_m) in hits:
            hx, hy = vue.convertir_coordonnees(hx_m, hy_m)
            pygame.draw.line(vue.screen, (180, 180, 180), (ox, oy), (hx, hy), 1)