from abc import ABC, abstractmethod


class Obstacle(ABC):
    """
    Classe abstraite définissant l'interface commune à tous les obstacles.

    Chaque obstacle doit implémenter :
        collision() : détecte si un robot (cercle) touche l'obstacle
        dessiner()  : affiche l'obstacle via la vue Pygame

    Sous-classe concrète utilisée dans ce projet :
        ObstacleRectangle — mur rectangulaire axis-aligned
    """

    @abstractmethod
    def collision(self, position, rayon_robot):
        """
        Retourne True si le cercle (position, rayon_robot) est en collision
        avec cet obstacle.

        Paramètres :
            position    : tuple (x, y) — centre du robot (mètres)
            rayon_robot : float — rayon du robot (mètres)
        """
        pass

    @abstractmethod
    def dessiner(self, vue):
        """
        Dessine l'obstacle sur l'écran via l'objet vue (VuePygame).

        Paramètre :
            vue : instance de VuePygame — fournit screen et les conversions de coordonnées
        """
        pass
