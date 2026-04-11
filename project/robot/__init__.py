"""
Package robot — Simulation de robots mobiles autonomes.

Ce package implémente une simulation complète avec deux robots autonomes
naviguant dans un environnement 2D avec obstacles, selon une architecture MVC.

Architecture :
    Modèle   → RobotMobile, Environnement, Colis, Zone, Batterie, FileAttenteColis
    Vue      → VuePygame (affichage Pygame)
    Contrôle → ControleurAuto (go-to-goal + évitement Lidar)

Modules :
    robot_mobile      : RobotMobile — position, orientation, moteur (encapsulation POO)
    moteur            : MoteurDifferentiel, MoteurOmnidirectionnel (polymorphisme ABC)
    environnement     : Environnement — monde, obstacles, physique des collisions
    ObstacleRectangle : obstacle rectangulaire — collision cercle + intersection Lidar
    obstacle          : classe abstraite Obstacle (interface commune)
    capteurs          : classe abstraite Capteur (interface commune)
    lidar             : Lidar 2D — N rayons, distances, points d'impact
    controleur_auto   : ControleurAuto — navigation autonome + anti-blocage
    Zone              : Zone non bloquante — stockage, export, charge
    Colis             : Colis — position, couleur, cycle de vie
    file_attente      : FileAttenteColis — convoyeur FIFO avec warmup
    robot2            : Robot2 — robot videur autonome (FSM + Lidar + collisions)
    batterie          : Batterie — niveau, recharge progressive, consommation
    vue               : VuePygame / VueTerminalRobot — rendu (couche Vue MVC)
"""
