from abc import ABC, abstractmethod

class Obstacle(ABC):
    @abstractmethod
    def collision(self, position, rayon_robot):
        pass

    @abstractmethod
    def dessiner(self, vue):
        pass