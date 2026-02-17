import pygame

class ObstacleRectangle:
    """
    Obstacle rectangle axis-aligned (non tourné) en mètres.
    (x, y) = centre, (largeur, hauteur) = dimensions.
    """
    def __init__(self, x, y, largeur, hauteur):
        self.x = float(x)
        self.y = float(y)
        self.largeur = float(largeur)
        self.hauteur = float(hauteur)

    @property
    def left(self):
        return self.x - self.largeur / 2

    @property
    def right(self):
        return self.x + self.largeur / 2

    @property
    def bottom(self):
        return self.y - self.hauteur / 2

    @property
    def top(self):
        return self.y + self.hauteur / 2

    def dessiner(self, vue):
        """
        La vue doit avoir rect_m_to_rect_px(...) et screen.
        """
        rect_px = vue.rect_m_to_rect_px(self.x, self.y, self.largeur, self.hauteur)
        pygame.draw.rect(vue.screen, (200, 60, 60), rect_px)
