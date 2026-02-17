import math
import pygame
from robot.obstacle import Obstacle

class ObstacleCercle(Obstacle):
    def __init__(self, x, y, rayon):
        self.x = float(x)
        self.y = float(y)
        self.rayon = float(rayon)

    def collision(self, position, rayon_robot):
        rx, ry = position
        d = math.sqrt((rx - self.x) ** 2 + (ry - self.y) ** 2)
        return d <= (self.rayon + rayon_robot)

    def dessiner(self, vue):
        # vue = VuePygame (on utilise sa conversion)
        px, py = vue.convertir_coordonnees(self.x, self.y)
        pr = int(self.rayon * vue.scale)
        pygame.draw.circle(vue.screen, (200, 60, 60), (px, py), pr)
