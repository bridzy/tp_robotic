import pygame


class Zone:
    """
    Zone non bloquante (pas de collision) : pickup ou storage.
    Les zones de stockage ont une capacité (capacity) et un compteur (count).
    Quand count >= capacity → is_full() = True → robot 2 est déclenché.
    """
    def __init__(self, name, x, y, largeur, hauteur, color_rgb, capacity=0):
        """
        Paramètres :
            name      : identifiant unique (ex: 'STORAGE_GREEN', 'CHARGE')
            x, y      : centre de la zone (mètres)
            color_rgb : couleur de fond (tuple RGB)
            capacity  : capacité max en colis (0 = illimitée)
        """
        self.name     = str(name)
        self.x        = float(x)
        self.y        = float(y)
        self.largeur  = float(largeur)
        self.hauteur  = float(hauteur)
        self.color    = tuple(color_rgb)
        self.capacity = int(capacity)   # 0 = pas de limite (ex: zone export)
        self.count    = 0               # colis actuellement dans la zone

    # ------------------------------------------------------------------
    # Gestion capacité
    # ------------------------------------------------------------------
    def is_full(self):
        """Retourne True si la zone a atteint sa capacité."""
        if self.capacity <= 0:
            return False
        return self.count >= self.capacity

    def add_colis(self):
        """Ajoute 1 colis. Retourne True si ok, False si pleine."""
        if self.is_full():
            return False
        self.count += 1
        return True

    def vider(self):
        """Robot 2 vide la zone → remet count à 0."""
        taken = self.count
        self.count = 0
        return taken

    # ------------------------------------------------------------------
    # Dessin
    # ------------------------------------------------------------------
    def dessiner(self, vue):
        """Dessine la zone et, si elle a une capacité, le compteur x/capacity."""
        r = vue.rect_m_to_rect_px(self.x, self.y, self.largeur, self.hauteur)
        pygame.draw.rect(vue.screen, self.color, r)

        # Contour rouge si pleine
        if self.is_full():
            pygame.draw.rect(vue.screen, (220, 0, 0), r, 3)
        else:
            pygame.draw.rect(vue.screen, (80, 80, 80), r, 1)

        # Compteur x/capacity
        if self.capacity > 0:
            font = pygame.font.SysFont("arial", 15, bold=True)
            txt = font.render(f"{self.count}/{self.capacity}", True, (20, 20, 20))
            txt_rect = txt.get_rect(center=r.center)
            vue.screen.blit(txt, txt_rect)
