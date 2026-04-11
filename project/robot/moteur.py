import math
from abc import ABC, abstractmethod


class Moteur(ABC):
    """
    Classe abstraite définissant l'interface commune à tous les moteurs.

    Principe de substitution (Liskov) : tout objet Moteur peut être
    branché sur un RobotMobile sans que le robot ait besoin de savoir
    quel type de moteur il utilise.

    Sous-classes concrètes :
        MoteurDifferentiel    : 2 roues (v, omega) — utilisé dans ce projet
        MoteurOmnidirectionnel: 4 roues (vx, vy, omega) — prévu pour extension
    """

    @abstractmethod
    def commander(self, **kwargs):
        """Reçoit les consignes de vitesse (v, omega ou vx, vy, omega)."""
        pass

    @abstractmethod
    def mettre_a_jour(self, robot, dt):
        """Applique le déplacement au robot pour un pas de temps dt (secondes)."""
        pass


class MoteurDifferentiel(Moteur):
    """
    Moteur à entraînement différentiel — modèle cinématique unicycle.

    Commandes :
        v     : vitesse linéaire (m/s) — avance/recule
        omega : vitesse angulaire (rad/s) — tourne à gauche/droite

    Modèle cinématique appliqué à chaque tick :
        orientation(t+dt) = orientation(t) + omega * dt
        x(t+dt)           = x(t) + v * cos(orientation(t)) * dt
        y(t+dt)           = y(t) + v * sin(orientation(t)) * dt
    """

    def __init__(self):
        """Initialise les consignes v et omega à zéro."""
        self.v     = 0.0   # vitesse linéaire courante (m/s)
        self.omega = 0.0   # vitesse angulaire courante (rad/s)

    def commander(self, **kwargs):
        """Met à jour les consignes v et omega."""
        self.v     = float(kwargs.get("v",     self.v))
        self.omega = float(kwargs.get("omega", self.omega))

    def mettre_a_jour(self, robot, dt):
        """Intègre le mouvement différentiel sur dt secondes."""
        dt      = float(dt)
        theta_k = robot.orientation
        robot.orientation = (robot.orientation + self.omega * dt) % (2 * math.pi)
        robot.x           = robot.x + self.v * math.cos(theta_k) * dt
        robot.y           = robot.y + self.v * math.sin(theta_k) * dt


class MoteurOmnidirectionnel(Moteur):
    """
    Moteur omnidirectionnel — le robot peut se déplacer dans toutes
    les directions indépendamment de son orientation.

    Commandes :
        vx    : vitesse selon l'axe local X du robot (m/s)
        vy    : vitesse selon l'axe local Y du robot (m/s)
        omega : vitesse angulaire (rad/s)

    Non utilisé dans la version actuelle du projet, mais présent pour
    illustrer le polymorphisme : on peut substituer ce moteur à
    MoteurDifferentiel sans modifier RobotMobile.
    """

    def __init__(self):
        """Initialise les consignes vx, vy et omega à zéro."""
        self.vx    = 0.0
        self.vy    = 0.0
        self.omega = 0.0

    def commander(self, **kwargs):
        """Met à jour les consignes vx, vy et omega."""
        self.vx    = float(kwargs.get("vx",    self.vx))
        self.vy    = float(kwargs.get("vy",    self.vy))
        self.omega = float(kwargs.get("omega", self.omega))

    def mettre_a_jour(self, robot, dt):
        """Intègre le mouvement omnidirectionnel sur dt secondes."""
        dt      = float(dt)
        theta_k = robot.orientation
        robot.orientation = (robot.orientation + self.omega * dt) % (2 * math.pi)
        robot.x += (self.vx * math.cos(theta_k) - self.vy * math.sin(theta_k)) * dt
        robot.y += (self.vx * math.sin(theta_k) + self.vy * math.cos(theta_k)) * dt
