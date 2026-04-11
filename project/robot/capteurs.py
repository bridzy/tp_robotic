from abc import ABC, abstractmethod


class Capteur(ABC):
    """
    Classe abstraite définissant l'interface commune à tous les capteurs.

    Un capteur lit l'environnement autour du robot et retourne des données
    brutes (distances, images, etc.).

    Sous-classe concrète utilisée dans ce projet :
        Lidar — capteur de distance à balayage laser 2D
    """

    @abstractmethod
    def read(self, env, robot):
        """
        Lit les données du capteur dans l'environnement donné.

        Paramètres :
            env   : Environnement — fournit les obstacles et dimensions du monde
            robot : RobotMobile  — fournit la position et l'orientation

        Retourne un dictionnaire contenant les mesures (ex: distances, hits).
        """
        raise NotImplementedError

    def draw(self, vue, robot, data):
        """
        Affiche optionnellement les données du capteur (rayons Lidar, etc.).
        Méthode non abstraite : par défaut, ne fait rien.
        """
        return
