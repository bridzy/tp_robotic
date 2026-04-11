class PathFollower:
    """
    Suit une liste de waypoints (x,y). Quand un point est atteint, passe au suivant.
    finished() reste True tant qu'on n'a pas changé de chemin.
    """
    def __init__(self, seuil=0.35):
        self.seuil = float(seuil)
        self.waypoints = []
        self.i = 0
        self._finished = False

    def set_path(self, waypoints):
        self.waypoints = [(float(x), float(y)) for (x, y) in waypoints]
        self.i = 0
        self._finished = (len(self.waypoints) == 0)

    def clear(self):
        self.set_path([])

    def has_path(self):
        return self.i < len(self.waypoints)

    def finished(self):
        return self._finished

    def current_target(self):
        if self.has_path():
            return self.waypoints[self.i]
        return None

    def update(self, robot):
        """
        Si robot est proche du waypoint courant, on passe au suivant.
        Quand on dépasse le dernier => finished = True.
        """
        if not self.has_path():
            return

        tx, ty = self.waypoints[self.i]
        dx = tx - robot.x
        dy = ty - robot.y
        if (dx * dx + dy * dy) <= (self.seuil * self.seuil):
            self.i += 1
            if self.i >= len(self.waypoints):
                self._finished = True