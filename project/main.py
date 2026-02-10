import math
from robot.robot_mobile import RobotMobile
from robot.moteur import *

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


"""
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

"""


print(RobotMobile.moteur_valide(MoteurDifferentiel()))  # True
print(RobotMobile.moteur_valide("pas un moteur"))       # False

from robot.robot_mobile import RobotMobile

robot = RobotMobile()
print(robot)