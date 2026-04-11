"""
main.py — Simulation deux robots autonomes.

Robot 1 : collecte convoyeur → STORAGE_RED / STORAGE_GREEN
          Batterie : 100%, -25% par colis livré, recharge à ≤25% sur CHARGE zone
Robot 2 : vide les zones pleines → EXPORT (haut gauche)

Touches :
  H → lidar ON/OFF
  P → pause / reprise
"""

import math
import pygame 

from robot.robot_mobile      import RobotMobile
from robot.moteur            import MoteurDifferentiel
from robot.vue               import VuePygame
from robot.environnement     import Environnement
from robot.ObstacleRectangle import ObstacleRectangle
from robot.Zone              import Zone
from robot.lidar             import Lidar
from robot.controleur_auto   import ControleurAuto
from robot.file_attente      import FileAttenteColis
from robot.robot2            import Robot2
from robot.batterie          import Batterie
from robot.Colis             import Colis


# ======================================================================
# Constantes
# ======================================================================
PICK_RADIUS   = 0.45
DROP_RADIUS   = 0.55
CHARGE_RADIUS = 0.60    # distance pour commencer à charger
COLIS_OFFSET  = 0.38
ZONE_CAPACITY = 5
DT  = 0.1
FPS = 60

# États FSM Robot 1
R1_WORKING  = "WORKING"   # travail normal
R1_CHARGING = "CHARGING"  # va charger / est en charge


# ======================================================================
# Construction
# ======================================================================
def build_robot():
    """Crée et positionne Robot 1 à l'origine (0, 0) avec un MoteurDifferentiel."""
    robot = RobotMobile(moteur=MoteurDifferentiel(), rayon=0.25)
    robot.x, robot.y, robot.orientation = 0.0, 0.0, 0.0
    return robot


def _add_world_borders(env, ep=0.18):
    """
    Ajoute 4 murs fins sur les bordures du monde.
    Permet au Lidar de détecter les bords comme des obstacles normaux.
    """
    L, H = float(env.largeur), float(env.hauteur)
    env.ajouter_obstacle(ObstacleRectangle(x=0.0,  y=H/2,  largeur=L,  hauteur=ep))
    env.ajouter_obstacle(ObstacleRectangle(x=0.0,  y=-H/2, largeur=L,  hauteur=ep))
    env.ajouter_obstacle(ObstacleRectangle(x=-L/2, y=0.0,  largeur=ep, hauteur=H))
    env.ajouter_obstacle(ObstacleRectangle(x=L/2,  y=0.0,  largeur=ep, hauteur=H))


def build_environment():
    """
    Construit le monde complet : bordures, zones (stockage, export, charge),
    murs internes et convoyeur. Retourne l'Environnement configuré.
    """
    env = Environnement(largeur=10.0, hauteur=10.0)
    _add_world_borders(env)

    # Zones de stockage
    env.ajouter_zone(Zone("STORAGE_GREEN", x=-3.5, y=-3.5,
                          largeur=1.8, hauteur=1.8,
                          color_rgb=(130, 230, 130), capacity=ZONE_CAPACITY))
    env.ajouter_zone(Zone("STORAGE_RED",   x=3.5,  y=2.8,
                          largeur=1.8, hauteur=1.8,
                          color_rgb=(245, 130, 130), capacity=ZONE_CAPACITY))

    # Zone export Robot 2
    env.ajouter_zone(Zone("EXPORT", x=-4.0, y=4.0,
                          largeur=1.5, hauteur=1.5,
                          color_rgb=(180, 160, 230), capacity=0))

    # Zone de charge Robot 1 — centre gauche
    env.ajouter_zone(Zone("CHARGE", x=-3.8, y=0.0,
                          largeur=1.2, hauteur=1.2,
                          color_rgb=(255, 230, 80), capacity=0))

    # Murs internes
    ep = 0.18
    for m in [
        ObstacleRectangle(x=-1.0, y=1.5,  largeur=ep,  hauteur=3.5),
        ObstacleRectangle(x=-1.9, y=-0.3, largeur=2.0, hauteur=ep),
        ObstacleRectangle(x=-3.0, y=-2.0, largeur=4.0, hauteur=ep),
        ObstacleRectangle(x=3.25, y=4.2,  largeur=3.5, hauteur=ep),
        ObstacleRectangle(x=3.8,  y=1.5,  largeur=2.5, hauteur=ep),
        ObstacleRectangle(x=1.5,  y=-4, largeur=ep,  hauteur=2),
    ]:
        env.ajouter_obstacle(m)

    # Convoyeur
    env.file_attente = FileAttenteColis(
        center_x=3.55, center_y=-4.35,
        width=2.60, height=0.75,
        spawn_min_s=8.0, spawn_max_s=18.0,
        max_size=6, spacing=0.34,
        warmup_count=3, warmup_delay=2.0
    )


    return env


def build_vue():
    """Initialise et retourne la fenêtre Pygame (1100×750, scale 60 px/m)."""
    return VuePygame(
        largeur=1100, hauteur=750, scale=60,
        robot_image_path="robot.png",
        belt_image_path="fil.png"
    )


# ======================================================================
# Helpers
# ======================================================================
def _get_zone(env, name):
    """Retourne la Zone portant ce nom dans l'environnement, ou None."""
    for z in env.zones:
        if z.name == name:
            return z
    return None


def _dist2(ax, ay, bx, by):
    """Distance au carré entre deux points — évite un sqrt() inutile."""
    return (ax - bx) ** 2 + (ay - by) ** 2


def _colis_derriere_robot(robot):
    """Calcule la position du colis transporté, placé derrière le robot."""
    x = robot.x - COLIS_OFFSET * math.cos(robot.orientation)
    y = robot.y - COLIS_OFFSET * math.sin(robot.orientation)
    return x, y


# ======================================================================
# FSM Robot 1 — batterie
# ======================================================================
def update_batterie(env, robot, batterie):
    """
    Gère la FSM batterie de Robot 1 :
      WORKING  → si batterie ≤ 25% et colis déposé → passe en CHARGING
      CHARGING → navigue vers CHARGE, recharge, retourne WORKING à 100%
    Retourne la cible (tx, ty) si on est en mode charge, None sinon.
    """
    charge_zone = _get_zone(env, "CHARGE")

    if env._r1_state == R1_WORKING:
        # Déclencher la recharge si seuil atteint ET pas de colis en cours
        if batterie.needs_charge() and env.colis_transporte is None:
            env._r1_state = R1_CHARGING

    if env._r1_state == R1_CHARGING:
        if charge_zone is None:
            env._r1_state = R1_WORKING
            return None

        dist = math.hypot(robot.x - charge_zone.x, robot.y - charge_zone.y)

        if dist <= CHARGE_RADIUS:
            # Arrivé sur zone : stopper le robot et recharger
            robot.commander(v=0.0, omega=0.0)
            full = batterie.charger(DT)
            if full:
                env._r1_state = R1_WORKING   # batterie pleine → reprendre le travail
            return charge_zone.x, charge_zone.y   # cible = zone charge (maintenir)

        # Pas encore arrivé → naviguer vers la zone
        return charge_zone.x, charge_zone.y

    return None   # WORKING → pas de cible forcée


# ======================================================================
# FSM Robot 1 — cible normale
# ======================================================================
def compute_target(env, robot):
    """Cible de travail (hors charge)."""
    if env.colis_transporte is not None:
        z = _get_zone(env, f"STORAGE_{env.colis_transporte.couleur}")
        if z is None or z.is_full():
            return env.home
        return z.x, z.y

    if env.file_attente is not None and env.file_attente.has_waiting():
        return env.file_attente.pickup_point()

    return env.home


# ======================================================================
# FSM Robot 1 — prise / dépôt
# ======================================================================
def update_mission(env, robot, robot2, batterie):
    """Prise et dépôt de colis. Consomme la batterie à chaque livraison."""

    # Pas de mission si on charge
    if env._r1_state == R1_CHARGING:
        return

    if env.colis_transporte is not None:
        cx, cy = _colis_derriere_robot(robot)
        env.colis_transporte.set_position(cx, cy)

        z = _get_zone(env, f"STORAGE_{env.colis_transporte.couleur}")
        if z is not None and not z.is_full():
            if _dist2(robot.x, robot.y, z.x, z.y) <= DROP_RADIUS ** 2:
                z.add_colis()
                env.colis_transporte.etat = Colis.DELIVERED
                env.colis_transporte = None
                env.nb_livres += 1

                # Consommer batterie
                batterie.consommer()

                if z.is_full():
                    robot2.request_empty(z)
        return

    if env.file_attente is not None:
        picked = env.file_attente.try_pick_first(robot.x, robot.y, PICK_RADIUS)
        if picked is not None:
            env.colis_transporte = picked
            cx, cy = _colis_derriere_robot(robot)
            env.colis_transporte.set_position(cx, cy)


# ======================================================================
# Boucle principale
# ======================================================================
def game_loop(robot, robot2, env, vue, controleur, batterie):
    """
    Boucle principale de simulation (FPS images/seconde).
    Ordre par tick : événements → convoyeur → Robot 2 → batterie R1
    → mission R1 → contrôle R1 → physique → rendu.
    """
    running = True

    while running:
        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    vue.show_lidar = not vue.show_lidar
                if event.key == pygame.K_p:
                    env.paused = not env.paused

        if env.paused:
            vue.dessiner_environnement(env)
            vue.tick(FPS)
            continue

        # ── Update convoyeur ──
        env.file_attente.update(DT)

        # ── Robot 2 ──
        saved_robot = env.robot
        env.robot   = robot2.robot
        robot2.update(DT, robot1=robot)
        env.robot   = saved_robot

        # ── Robot 1 : batterie FSM ──
        charge_target = update_batterie(env, robot, batterie)

        # ── Robot 1 : mission ──
        update_mission(env, robot, robot2, batterie)

        # ── Robot 1 : contrôle + physique ──
        # Si on est EN CHARGE sur la zone → robot immobile, pas de contrôleur
        if env._r1_state == R1_CHARGING and charge_target is not None:
            dist_charge = math.hypot(robot.x - charge_target[0], robot.y - charge_target[1])
            if dist_charge <= CHARGE_RADIUS:
                # Robot sur zone : stopper complètement, ignorer le contrôleur
                robot.commander(v=0.0, omega=0.0)
                env._r1_vitesse = 0.0
                env.mettre_a_jour(DT)
            else:
                # Pas encore arrivé : naviguer vers la zone
                controleur.set_target(*charge_target)
                env.autres_robots = [(robot2.robot.x, robot2.robot.y, robot2.robot.rayon)]
                cmd = controleur.update(robot, env, DT)
                env.autres_robots = []
                env._r1_vitesse = abs(cmd.get("v", 0.0))
                robot.commander(**cmd)
                env.mettre_a_jour(DT)
        else:
            # Mode normal : calculer cible et naviguer
            tx, ty = compute_target(env, robot)
            controleur.set_target(tx, ty)
            # Rendre Robot 2 visible au Lidar de Robot 1
            env.autres_robots = [(robot2.robot.x, robot2.robot.y, robot2.robot.rayon)]
            cmd = controleur.update(robot, env, DT)
            env.autres_robots = []
            env._r1_vitesse = abs(cmd.get("v", 0.0))
            robot.commander(**cmd)
            env.mettre_a_jour(DT)

        if env.colis_transporte is not None:
            cx, cy = _colis_derriere_robot(robot)
            env.colis_transporte.set_position(cx, cy)

        # ── Exposer données à la vue ──
        env.robot2   = robot2
        env.batterie = batterie

        # ── Rendu ──
        vue.dessiner_environnement(env)
        vue.tick(FPS)


# ======================================================================
# Point d'entrée
# ======================================================================
def main():
    """Point d'entrée : construit tous les composants et lance la simulation."""
    robot = build_robot()
    env   = build_environment()
    vue   = build_vue()

    env.ajouter_robot(robot)
    env.home = (robot.x, robot.y)
    vue.set_zone(env.largeur, env.hauteur)

    lidar      = Lidar(n_rays=41, fov=math.radians(220), max_range=4.0)
    env.lidar_sensor = lidar
    controleur = ControleurAuto(lidar)

    export_zone = _get_zone(env, "EXPORT")
    robot2      = Robot2(export_zone=export_zone, env=env)

    batterie = Batterie(niveau_initial=100.0)

    game_loop(robot, robot2, env, vue, controleur, batterie)
    pygame.quit()


if __name__ == "__main__":
    main()
