import math
from robot.robot_mobile import RobotMobile
from robot.moteur import *
from robot.controleur import ControleurTerminal
from robot.vue import VueTerminalRobot
from robot.controleur import ControleurClavierPygame
from robot.vue import VuePygame
from robot.environnement import Environnement
from robot.obstacle_cercle import ObstacleCercle
from robot.ObstacleRectangle import ObstacleRectangle


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
    robot = RobotMobile(moteur=MoteurDifferentiel(), rayon=0.25)

    # Environnement (modèle)
    env = Environnement(largeur=10.0, hauteur=10.0)
    env.ajouter_robot(robot)

    # Obstacles CERCLES (dans env) -> dessin via obs.dessiner(vue)
    env.ajouter_obstacle(ObstacleCercle(x=2.0, y=1.0, rayon=0.6))
    
    env.ajouter_obstacle(ObstacleCercle(x=-1.5, y=-1.0, rayon=0.8))
    
    env.ajouter_obstacle(ObstacleRectangle(x=0.0, y=2.5, largeur=1.2, hauteur=0.6))
    env.ajouter_obstacle(ObstacleRectangle(x=-2.5, y=0.0, largeur=0.8, hauteur=2.0))
    env.ajouter_obstacle(ObstacleRectangle(x=2.5, y=-2.0, largeur=2.2, hauteur=0.7))


    # Contrôleur + Vue
    controleur = ControleurClavierPygame(v_max=2.0, omega_max=2.0)
    vue = VuePygame(largeur=800, hauteur=600, scale=50)

    # ✅ Zone (contour) = même taille que l'environnement
    vue.set_zone(env.largeur, env.hauteur)

    # ✅ Obstacles RECTANGLES (dessinés par la vue)
    # Format : (x, y, w, h) en mètres ; x,y = centre
    vue.set_obstacles([
        (0.0, 2.5, 1.2, 0.6),
        (-2.5, 0.0, 0.8, 2.0),
        (2.5, -2.0, 2.2, 0.7),
    ])

    dt = 0.1
    running = True

    while running:
        cmd = controleur.lire_commande()
        if cmd is None:
            running = False
            continue

        robot.commander(**cmd)
        env.mettre_a_jour(dt)              # collisions (si gérées dans env)
        vue.dessiner_environnement(env)    # affiche zone + obstacles + robot
        vue.tick(60)

    import pygame
    pygame.quit()


if __name__ == "__main__":
    main()