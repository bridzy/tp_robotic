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
        """
        Principe TP:
        1) sauvegarder état robot
        2) robot calcule son mouvement
        3) tester collision
        4) si collision => annuler déplacement
        """
        if self.robot is None:
            return

        # 1) sauvegarde
        x0, y0, th0 = self.robot.x, self.robot.y, self.robot.orientation

        # 2) mise à jour robot
        self.robot.mettre_a_jour(dt)

        # 3-4) collision => rollback
        if self.collision():
            self.robot.x, self.robot.y, self.robot.orientation = x0, y0, th0
