import pygame

class ObstacleRectangle:
    """
    Rectangle axis-aligned en mètres (non tourné).
    (x, y) = centre ; (largeur, hauteur) = dimensions.
    """
    def __init__(self, x, y, largeur, hauteur):
        """
        Paramètres :
            x, y            : centre du rectangle (mètres)
            largeur, hauteur : dimensions (mètres)
        """
        self.x = float(x)
        self.y = float(y)
        self.largeur = float(largeur)
        self.hauteur = float(hauteur)

    @property
    def left(self):
        """Bord gauche du rectangle (mètres)."""
        return self.x - self.largeur / 2

    @property
    def right(self):
        """Bord droit du rectangle (mètres)."""
        return self.x + self.largeur / 2

    @property
    def bottom(self):
        """Bord bas du rectangle (mètres)."""
        return self.y - self.hauteur / 2

    @property
    def top(self):
        """Bord haut du rectangle (mètres)."""
        return self.y + self.hauteur / 2

    # -----------------------------
    # Collision cercle-rectangle
    # -----------------------------
    def collision(self, pos, r):
        """Collision cercle (robot) vs rectangle."""
        cx, cy = pos

        nearest_x = max(self.left, min(cx, self.right))
        nearest_y = max(self.bottom, min(cy, self.top))

        dx = cx - nearest_x
        dy = cy - nearest_y
        return (dx * dx + dy * dy) <= (r * r)

    # -----------------------------
    # Intersection rayon-rectangle (Lidar)
    # -----------------------------
    def intersection(self, ox, oy, dx, dy, max_range):
        """
        Intersection d'un rayon paramétré:
          P(t) = (ox, oy) + t*(dx, dy), t>=0
        avec un rectangle axis-aligned.
        Retourne t (distance le long du rayon) ou None.

        Utilise la méthode "slab" (stable et simple).
        """
        t_min = 0.0
        t_max = float(max_range)

        x_min = self.left
        x_max = self.right
        y_min = self.bottom
        y_max = self.top

        # Axe X
        if abs(dx) < 1e-9:
            if ox < x_min or ox > x_max:
                return None
        else:
            tx1 = (x_min - ox) / dx
            tx2 = (x_max - ox) / dx
            if tx1 > tx2:
                tx1, tx2 = tx2, tx1
            t_min = max(t_min, tx1)
            t_max = min(t_max, tx2)
            if t_min > t_max:
                return None

        # Axe Y
        if abs(dy) < 1e-9:
            if oy < y_min or oy > y_max:
                return None
        else:
            ty1 = (y_min - oy) / dy
            ty2 = (y_max - oy) / dy
            if ty1 > ty2:
                ty1, ty2 = ty2, ty1
            t_min = max(t_min, ty1)
            t_max = min(t_max, ty2)
            if t_min > t_max:
                return None

        # On veut la première intersection "devant" le rayon
        if 0.0 < t_min <= max_range:
            return t_min
        return None

    # -----------------------------
    # Dessin
    # -----------------------------
    def dessiner(self, vue):
        """Dessine le mur en noir."""
        rect_px = vue.rect_m_to_rect_px(self.x, self.y, self.largeur, self.hauteur)
        pygame.draw.rect(vue.screen, (0, 0, 0), rect_px)