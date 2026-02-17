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

    def dessiner_robot(self, robot):
        self.screen.fill((255, 255, 255))  # fond blanc

        x, y = self.convertir_coordonnees(robot.x, robot.y)
        r = 12  # rayon en pixels

        # robot = cercle
        pygame.draw.circle(self.screen, (0, 120, 255), (x, y), r)

        # orientation = trait
        x_dir = x + int(r * math.cos(robot.orientation))
        y_dir = y - int(r * math.sin(robot.orientation))
        pygame.draw.line(self.screen, (0, 0, 0), (x, y), (x_dir, y_dir), 2)

        pygame.display.flip()

    def tick(self, fps=60):
        self.clock.tick(fps)