import math
from abc import ABC, abstractmethod

class Moteur(ABC):
    @abstractmethod
    def commander(self, **kwargs):
        pass

    @abstractmethod
    def mettre_a_jour(self, robot, dt):
        pass


class MoteurDifferentiel(Moteur):
    def __init__(self):
        self.v = 0.0
        self.omega = 0.0

    def commander(self, **kwargs):
        # attend v et omega
        self.v = float(kwargs.get("v", self.v))
        self.omega = float(kwargs.get("omega", self.omega))

    def mettre_a_jour(self, robot, dt):
        dt = float(dt)
        theta_k = robot.orientation
        robot.orientation = robot.orientation + self.omega * dt
        robot.x = robot.x + self.v * math.cos(theta_k) * dt
        robot.y = robot.y + self.v * math.sin(theta_k) * dt


class MoteurOmnidirectionnel(Moteur):
    def __init__(self):
        self.vx = 0.0
        self.vy = 0.0
        self.omega = 0.0

    def commander(self, **kwargs):
        # attend vx, vy, omega
        self.vx = float(kwargs.get("vx", self.vx))
        self.vy = float(kwargs.get("vy", self.vy))
        self.omega = float(kwargs.get("omega", self.omega))

    def mettre_a_jour(self, robot, dt):
        dt = float(dt)
        theta_k = robot.orientation

        robot.orientation = robot.orientation + self.omega * dt

        robot.x = robot.x + (self.vx * math.cos(theta_k) - self.vy * math.sin(theta_k)) * dt
        robot.y = robot.y + (self.vx * math.sin(theta_k) + self.vy * math.cos(theta_k)) * dt