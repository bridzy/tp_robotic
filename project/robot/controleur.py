from abc import ABC, abstractmethod
import pygame

class Controleur(ABC):
    @abstractmethod
    def lire_commande(self):
        """Retourne une commande pour le robot (dict)"""
        pass


class ControleurTerminal(Controleur):
    def lire_commande(self):
        print("Commande differentiel : v omega (ex: 1.0 0.5)")
        entree = input("> ").strip()

        # Entrée vide => on arrête la simulation
        if entree == "":
            return None

        morceaux = entree.split()
        if len(morceaux) != 2:
            print("Format invalide. Exemple attendu : 1.0 0.5")
            return {}

        try:
            v = float(morceaux[0])
            omega = float(morceaux[1])
        except ValueError:
            print("Valeurs invalides. Exemple attendu : 1.0 0.5")
            return {}

        return {"v": v, "omega": omega}
    

class ControleurClavierPygame(Controleur):
    def __init__(self, v_max=2.0, omega_max=2.0):
        self.v_max = float(v_max)
        self.omega_max = float(omega_max)

    def lire_commande(self):
        # important: laisser pygame traiter les évènements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None  # stop

        keys = pygame.key.get_pressed()

        v = 0.0
        omega = 0.0

        # flèches: haut/bas => vitesse linéaire ; gauche/droite => rotation
        if keys[pygame.K_UP]:
            v += self.v_max
        if keys[pygame.K_DOWN]:
            v -= self.v_max
        if keys[pygame.K_LEFT]:
            omega += self.omega_max
        if keys[pygame.K_RIGHT]:
            omega -= self.omega_max

        return {"v": v, "omega": omega}
