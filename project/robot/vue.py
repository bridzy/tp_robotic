import math
import pygame


class VueTerminalRobot:
    def dessiner_robot(self, robot):
        print(f"Robot -> x={robot.x:.2f}, y={robot.y:.2f}, orientation={robot.orientation:.2f}")


class VuePygame:
    def __init__(self, largeur=800, hauteur=600, scale=50):
        pygame.init()
        self.screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("Simulation Robot Mobile")

        self.largeur = int(largeur)
        self.hauteur = int(hauteur)
        self.scale = float(scale)  # mètres -> pixels
        self.clock = pygame.time.Clock()

        # Zone (en mètres) : largeur/hauteur du terrain (rectangle centré en (0,0))
        self.zone_w_m = 10.0
        self.zone_h_m = 8.0

        # Obstacles "simples" : rectangles en mètres (x, y, w, h)
        # x,y = centre du rectangle en mètres
        self.obstacles = []

    # -----------------------------
    # Config zone + obstacles
    # -----------------------------
    def set_zone(self, largeur_m, hauteur_m):
        self.zone_w_m = float(largeur_m)
        self.zone_h_m = float(hauteur_m)

    def set_obstacles(self, obstacles):
        """
        obstacles : list[tuple(x, y, w, h)] en mètres
        x,y = centre ; w,h = dimensions
        """
        self.obstacles = list(obstacles)

    # -----------------------------
    # Conversions coordonnées
    # -----------------------------
    def convertir_coordonnees(self, x, y):
        """Convertit (mètres) -> (pixels) avec (0,0) au centre de l'écran."""
        px = int(self.largeur / 2 + (float(x) * self.scale))
        py = int(self.hauteur / 2 - (float(y) * self.scale))
        return px, py

    def rect_m_to_rect_px(self, x_m, y_m, w_m, h_m):
        """Rectangle en mètres (centre + dimensions) -> pygame.Rect en pixels."""
        cx, cy = self.convertir_coordonnees(x_m, y_m)
        w_px = max(1, int(float(w_m) * self.scale))
        h_px = max(1, int(float(h_m) * self.scale))

        left = cx - w_px // 2
        top = cy - h_px // 2
        return pygame.Rect(left, top, w_px, h_px)

    # -----------------------------
    # Dessin environnement (MVC)
    # -----------------------------
    def dessiner_environnement(self, env):
        """
        Dessine le monde complet :
        - fond
        - zone
        - obstacles
        - robot
        env peut contenir:
          env.obstacles : liste d'objets avec obs.dessiner(vue)
          env.robot : RobotMobile
        """
        # 1) fond
        self.screen.fill((255, 255, 255))

        # 2) zone (contour)
        self.dessiner_zone()

        # 3) obstacles (2 possibilités)
        # A) obstacles "objets" (si tu as déjà des classes Obstacle avec dessiner(vue))
        for obs in getattr(env, "obstacles", []):
            # si l'obstacle a une méthode dessiner, on l'utilise
            if hasattr(obs, "dessiner"):
                obs.dessiner(self)

        # B) obstacles simples stockés dans la vue (tu peux les définir via set_obstacles)
        self.dessiner_obstacles_rectangles()

        # 4) robot
        if getattr(env, "robot", None) is not None:
            self.dessiner_robot(env.robot)

        # 5) afficher une seule fois par frame
        pygame.display.flip()

    # -----------------------------
    # Dessin des éléments
    # -----------------------------
    def dessiner_zone(self):
        """Dessine le contour du terrain (rectangle centré en (0,0))."""
        zone_rect = self.rect_m_to_rect_px(
            x_m=0.0, y_m=0.0,
            w_m=self.zone_w_m, h_m=self.zone_h_m
        )
        pygame.draw.rect(self.screen, (0, 0, 0), zone_rect, 2)

    def dessiner_obstacles_rectangles(self):
        """Dessine les obstacles rectangles (liste self.obstacles)."""
        for (ox, oy, ow, oh) in self.obstacles:
            r = self.rect_m_to_rect_px(ox, oy, ow, oh)
            pygame.draw.rect(self.screen, (200, 60, 60), r)

    def dessiner_robot(self, robot):
        """Dessine le robot (cercle + trait orientation)."""
        x, y = self.convertir_coordonnees(robot.x, robot.y)

        # rayon robot: si robot.rayon existe => conversion mètres->pixels, sinon valeur par défaut
        if hasattr(robot, "rayon"):
            r = max(3, int(float(robot.rayon) * self.scale))
        else:
            r = 12

        # robot = cercle bleu
        pygame.draw.circle(self.screen, (0, 120, 255), (x, y), r)

        # orientation = trait noir
        x_dir = x + int(r * math.cos(robot.orientation))
        y_dir = y - int(r * math.sin(robot.orientation))
        pygame.draw.line(self.screen, (0, 0, 0), (x, y), (x_dir, y_dir), 2)

    # -----------------------------
    # Tick / FPS
    # -----------------------------
    def tick(self, fps=60):
        self.clock.tick(int(fps))
