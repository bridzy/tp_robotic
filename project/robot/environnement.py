def clamp(v, vmin, vmax):
    return max(vmin, min(v, vmax))

def collision_cercle_rectangle(cx, cy, r, rect):
    # point le plus proche du centre du cercle sur le rectangle
    nearest_x = clamp(cx, rect.left, rect.right)
    nearest_y = clamp(cy, rect.bottom, rect.top)

    dx = cx - nearest_x
    dy = cy - nearest_y
    return (dx * dx + dy * dy) <= (r * r)

class Environnement:
    def __init__(self, largeur=10.0, hauteur=10.0):
        # taille du monde en "mètres" (simple)
        self.largeur = float(largeur)
        self.hauteur = float(hauteur)
        self.robot = None
        self.obstacles = []

    def ajouter_robot(self, robot):
        self.robot = robot

    def ajouter_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def collision(self):
        """Retourne True si le robot est en collision (obstacles ou limites)."""
        if self.robot is None:
            return False

        # 1) collision avec les limites du monde (optionnel mais propre)
        x, y = self.robot.x, self.robot.y
        r = self.robot.rayon
        if (x - r < -self.largeur / 2) or (x + r > self.largeur / 2) or (y - r < -self.hauteur / 2) or (y + r > self.hauteur / 2):
            return True

        # 2) collision avec obstacles (polymorphisme)
        for obs in self.obstacles:
            if obs.collision((x, y), r):
                return True

        return False

    def mettre_a_jour(self, dt):
    # --- Sauvegarde avant mouvement
        old_x = self.robot.x
        old_y = self.robot.y
        old_theta = self.robot.orientation

    # --- Update robot (comme tu fais déjà)
        self.robot.mettre_a_jour(dt)

    # --- Collisions
        r = getattr(self.robot, "rayon", 0.25)

        for obs in self.obstacles:
        # Rectangle
            if obs.__class__.__name__ == "ObstacleRectangle":
                if collision_cercle_rectangle(self.robot.x, self.robot.y, r, obs):
                    self.robot.x = old_x
                    self.robot.y = old_y
                    self.robot.orientation = old_theta
                    break

        # Cercle (si tu as déjà ton test, garde-le)
            if obs.__class__.__name__ == "ObstacleCercle":
                dx = self.robot.x - obs.x
                dy = self.robot.y - obs.y
                if (dx * dx + dy * dy) <= (r + obs.rayon) ** 2:
                    self.robot.x = old_x
                    self.robot.y = old_y
                    self.robot.orientation = old_theta
                    break

    # --- Collision avec la zone (murs) (optionnel mais recommandé)
        demi_L = self.largeur / 2
        demi_H = self.hauteur / 2
        if (self.robot.x - r < -demi_L or self.robot.x + r > demi_L or
            self.robot.y - r < -demi_H or self.robot.y + r > demi_H):
            self.robot.x = old_x
            self.robot.y = old_y
            self.robot.orientation = old_theta
