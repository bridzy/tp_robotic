import math

class RobotMobile:
    _nb_robots = 0
    def __init__(self, x=0.0, y=0.0, orientation=0.0, moteur=None):
        self.__x = float(x)
        self.__y = float(y)
        self.__orientation = float(orientation)
        self.moteur = moteur  # objet moteur (peut être None)
        RobotMobile._nb_robots += 1


    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = float(value)

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = float(value)

    @property
    def orientation(self):
        return self.__orientation

    @orientation.setter
    def orientation(self, value):
        self.__orientation = float(value)

    def afficher(self):
        print(f"RobotMobile(x={self.x:.3f}, y={self.y:.3f}, orientation={self.orientation:.3f} rad)")

    # (optionnel) garder les méthodes simples
    def avancer(self, distance):
        distance = float(distance)
        self.x = self.x + distance * math.cos(self.orientation)
        self.y = self.y + distance * math.sin(self.orientation)

    def tourner(self, angle):
        angle = float(angle)
        self.orientation = (self.orientation + angle) % (2 * math.pi)

    # nouvelles méthodes liées au moteur
    def commander(self, **kwargs):
        if self.moteur is None:
            raise ValueError("Aucun moteur attaché au robot.")
        self.moteur.commander(**kwargs)

    def mettre_a_jour(self, dt):
        if self.moteur is None:
            raise ValueError("Aucun moteur attaché au robot.")
        self.moteur.mettre_a_jour(self, dt)
    
    @classmethod
    def nombre_robots(cls):
        return cls._nb_robots
    @staticmethod
    def moteur_valide(moteur):
        # Import local pour éviter dépendance circulaire
        from robot.moteur import Moteur
        return isinstance(moteur, Moteur)

    def __str__(self):
        return f"RobotMobile(x={self.x:.3f}, y={self.y:.3f}, orientation={self.orientation:.3f} rad)"