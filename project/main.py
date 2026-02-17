import math
from robot.robot_mobile import RobotMobile
from robot.moteur import *
from robot.controleur import ControleurTerminal
from robot.vue import VueTerminalRobot
from robot.controleur import ControleurClavierPygame
from robot.vue import VuePygame

#TP1 : 
"""
robot = RobotMobile()
print("Robot cree :", robot.x, robot.y, robot.orientation)
robot.afficher()
#robot.avancer(1.0)
#robot.afficher()

#robot.tourner(math.pi / 4)  # 45°
#robot.afficher()

#robot.avancer(3.0)
#robot.afficher()

#print(robot.__x)
#print(robot.x)



robot = RobotMobile(moteur=MoteurDifferentiel())
robot.commander(v=1.0, omega=0.5)  # vitesse + rotation
for _ in range(5):
    robot.mettre_a_jour(dt=1.0)    # 1 seconde
    robot.afficher()



robot = RobotMobile(moteur=MoteurOmnidirectionnel())
robot.afficher()

robot.commander(vx=1.0, vy=0.3, omega=0.2)
for _ in range(5):
    robot.mettre_a_jour(dt=1.0)
    robot.afficher()


r1 = RobotMobile()
r2 = RobotMobile()
print("Nombre de robots :", RobotMobile.nombre_robots())



print(RobotMobile.moteur_valide(MoteurDifferentiel()))  # True
print(RobotMobile.moteur_valide("pas un moteur"))       # False

from robot.robot_mobile import RobotMobile

robot = RobotMobile()
print(robot)

"""

# TP 2

def main():
    robot = RobotMobile(moteur=MoteurDifferentiel())
    controleur = ControleurClavierPygame(v_max=2.0, omega_max=2.0)
    vue = VuePygame(largeur=800, hauteur=600, scale=50)

    dt = 0.1  # 0.1s par frame (plus fluide que 1.0)
    running = True

    while running:
        # 1) lire les commandes clavier
        cmd = controleur.lire_commande()
        if cmd is None:
            running = False
            continue

        # 2) appliquer commande + update modèle
        robot.commander(**cmd)
        robot.mettre_a_jour(dt)

        # 3) affichage
        vue.dessiner_robot(robot)
        vue.tick(fps=60)

    # fermeture propre
    import pygame
    pygame.quit()
    print("Simulation terminée.")

if __name__ == "__main__":
    main()