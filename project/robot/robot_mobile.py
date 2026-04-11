import math


class RobotMobile:
    """
    Modèle cinématique d'un robot mobile à motorisation différentielle.

    Encapsule la position (x, y), l'orientation (en radians) et le rayon
    du robot. Délègue le calcul du mouvement à un objet Moteur.

    Les attributs x, y, orientation et rayon sont protégés par des
    @property pour garantir qu'ils restent toujours des float valides.

    Attribut de classe :
        _nb_robots : compteur du nombre total de robots créés (pattern classmethod)
    """

    _nb_robots = 0   # compteur de classe — incrémenté à chaque instanciation

    def __init__(self, x=0.0, y=0.0, orientation=0.0, moteur=None, rayon=0.25):
        """
        Paramètres :
            x, y        : position initiale (mètres)
            orientation : cap initial (radians)
            moteur      : instance de Moteur (MoteurDifferentiel, etc.)
            rayon       : rayon du robot pour la détection de collision (mètres)
        """
        self.__x           = float(x)
        self.__y           = float(y)
        self.__orientation = float(orientation)
        self.__rayon       = float(rayon)
        self.moteur        = moteur
        RobotMobile._nb_robots += 1

    # ------------------------------------------------------------------
    # Properties — encapsulation des attributs privés
    # ------------------------------------------------------------------
    @property
    def x(self):
        """Position X du robot (mètres)."""
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = float(value)

    @property
    def y(self):
        """Position Y du robot (mètres)."""
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = float(value)

    @property
    def orientation(self):
        """Cap du robot (radians, 0 = axe X positif)."""
        return self.__orientation

    @orientation.setter
    def orientation(self, value):
        self.__orientation = float(value)

    @property
    def rayon(self):
        """Rayon du robot (mètres), utilisé pour les collisions."""
        return self.__rayon

    @rayon.setter
    def rayon(self, value):
        self.__rayon = float(value)

    # ------------------------------------------------------------------
    # Méthodes de déplacement direct (sans moteur)
    # Conservées à titre pédagogique pour illustrer la cinématique de base.
    # Dans la simulation complète, c'est le Moteur qui pilote le mouvement.
    # ------------------------------------------------------------------
    def avancer(self, distance):
        """Déplace le robot en ligne droite selon son orientation actuelle."""
        distance = float(distance)
        self.x += distance * math.cos(self.orientation)
        self.y += distance * math.sin(self.orientation)

    def tourner(self, angle):
        """Fait pivoter le robot d'un angle donné (radians)."""
        self.orientation = (self.orientation + float(angle)) % (2 * math.pi)

    def afficher(self):
        """Affiche l'état du robot dans le terminal (debug)."""
        print(f"RobotMobile(x={self.x:.3f}, y={self.y:.3f}, "
              f"orientation={self.orientation:.3f} rad)")

    # ------------------------------------------------------------------
    # Méthodes liées au moteur (utilisées dans la simulation)
    # ------------------------------------------------------------------
    def commander(self, **kwargs):
        """
        Transmet une commande au moteur (ex: v=0.5, omega=0.3).
        Lève ValueError si aucun moteur n'est attaché.
        """
        if self.moteur is None:
            raise ValueError("Aucun moteur attaché au robot.")
        self.moteur.commander(**kwargs)

    def mettre_a_jour(self, dt):
        """
        Demande au moteur de calculer et appliquer le déplacement pour dt secondes.
        Appelé par Environnement.mettre_a_jour() à chaque tick.
        """
        if self.moteur is None:
            raise ValueError("Aucun moteur attaché au robot.")
        self.moteur.mettre_a_jour(self, dt)

    # ------------------------------------------------------------------
    # Méthodes de classe et statiques
    # ------------------------------------------------------------------
    @classmethod
    def nombre_robots(cls):
        """Retourne le nombre total de robots instanciés (compteur de classe)."""
        return cls._nb_robots

    @staticmethod
    def moteur_valide(moteur):
        """Vérifie qu'un objet est bien une instance de Moteur (isinstance)."""
        from robot.moteur import Moteur
        return isinstance(moteur, Moteur)

    # ------------------------------------------------------------------
    # Représentation
    # ------------------------------------------------------------------
    def __str__(self):
        """Représentation lisible pour print() et le terminal."""
        return (f"RobotMobile(x={self.x:.3f}, y={self.y:.3f}, "
                f"orientation={self.orientation:.3f} rad)")
