import math
import pygame


class VueTerminalRobot:
    def dessiner_robot(self, robot):
        # Affichage simple de l'état du robot
        print(f"Robot -> x={robot.x:.2f}, y={robot.y:.2f}, orientation={robot.orientation:.2f}")


class VuePygame:
    def __init__(self, largeur=800, hauteur=600, scale=50):
        pygame.init()
        self.screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("Simulation Robot Mobile")
        self.largeur = largeur
        self.hauteur = hauteur
        self.scale = scale  # metres -> pixels
        self.clock = pygame.time.Clock()

    def convertir_coordonnees(self, x, y):
        # centre écran + conversion metres->pixels
        px = int(self.largeur / 2 + (x * self.scale))
        py = int(self.hauteur / 2 - (y * self.scale))
        return px, py

    def dessiner_environnement(self, env):
        # 1) fond
        self.screen.fill((255, 255, 255))

        # 2) obstacles
        for obs in getattr(env, "obstacles", []):
            obs.dessiner(self)

        # 3) robot
        if getattr(env, "robot", None) is not None:
            self.dessiner_robot(env.robot)

        # 4) afficher une seule fois par frame
        pygame.display.flip()

    def dessiner_robot(self, robot):
        # IMPORTANT: ne pas faire screen.fill() ici (sinon ça efface les obstacles)
        x, y = self.convertir_coordonnees(robot.x, robot.y)

        # rayon robot: si robot.rayon existe => conversion mètres->pixels, sinon valeur par défaut
        if hasattr(robot, "rayon"):
            r = max(3, int(robot.rayon * self.scale))
        else:
            r = 12

        # robot = cercle bleu
        pygame.draw.circle(self.screen, (0, 120, 255), (x, y), r)

        # orientation = trait noir
        x_dir = x + int(r * math.cos(robot.orientation))
        y_dir = y - int(r * math.sin(robot.orientation))
        pygame.draw.line(self.screen, (0, 0, 0), (x, y), (x_dir, y_dir), 2)

    def tick(self, fps=60):
        self.clock.tick(fps)