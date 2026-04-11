"""
robot2.py — Robot videur autonome (Robot 2).

Vrai RobotMobile + Lidar + ControleurAuto + collisions murs + collision inter-robots.

FSM :
  IDLE      → immobile à la zone EXPORT
  GO_ZONE   → navigue vers la zone saturée
  PICK      → vide la zone instantanément → GO_EXPORT
  GO_EXPORT → navigue vers la zone EXPORT
  DROP      → dépose les colis → IDLE ou prochain en file
"""

import math
from collections import deque

from robot.robot_mobile    import RobotMobile
from robot.moteur          import MoteurDifferentiel
from robot.lidar           import Lidar
from robot.controleur_auto import ControleurAuto

ARRIVE_RADIUS = 0.55   # distance pour considérer "arrivé" sur une zone


class Robot2:
    """
    Robot videur autonome équipé d'un RobotMobile, d'un Lidar et d'un
    ControleurAuto. Surveille les zones de stockage et les vide quand
    elles atteignent leur capacité maximale.
    """
    IDLE      = "IDLE"
    GO_ZONE   = "GO_ZONE"
    PICK      = "PICK"
    GO_EXPORT = "GO_EXPORT"
    DROP      = "DROP"

    def __init__(self, export_zone, env):
        """
        Paramètres :
            export_zone : Zone de stationnement et de dépôt (haut gauche)
            env         : Environnement — pour le Lidar et les collisions
        """
        self.export_zone = export_zone
        self.env         = env

        # Vrai robot mobile
        self.robot = RobotMobile(moteur=MoteurDifferentiel(), rayon=0.22)
        self.robot.x           = float(export_zone.x)
        self.robot.y           = float(export_zone.y)
        self.robot.orientation = 0.0

        # Lidar dédié
        self.lidar = Lidar(n_rays=31, fov=math.radians(200), max_range=3.0)

        # Contrôleur autonome
        self.controleur = ControleurAuto(self.lidar)
        self.controleur.v_max       = 0.20
        self.controleur.v_min       = 0.10
        self.controleur.omega_max   = 0.85
        self.controleur.v_near_wall = 0.18
        self.controleur.v_turn      = 0.15
        self.controleur.alpha_v     = 0.22
        self.controleur.alpha_w     = 0.22

        # FSM
        self.state       = Robot2.IDLE
        self.target_zone = None
        self.carry       = 0

        # File d'attente
        self._queue    = deque()
        self._in_queue = set()

        # Stats
        self.total_exported = 0

        # Lidar data pour affichage
        self.lidar_data = None

        # Vitesse instantanée (pour HUD)
        self.vitesse = 0.0

    # ------------------------------------------------------------------
    # Proxies pour la vue
    # ------------------------------------------------------------------
    @property
    def x(self):
        """Position X de Robot 2 (proxy vers self.robot.x)."""
        return self.robot.x
    @property
    def y(self):
        """Position Y de Robot 2 (proxy vers self.robot.y)."""
        return self.robot.y
    @property
    def orientation(self):
        """Orientation de Robot 2 en radians."""
        return self.robot.orientation
    @property
    def is_idle(self):
        """True si Robot 2 est en attente (état IDLE)."""
        return self.state == Robot2.IDLE

    # ------------------------------------------------------------------
    # Interface publique
    # ------------------------------------------------------------------
    def request_empty(self, zone):
        """
        Appelé par Robot 1 quand une zone atteint sa capacité.
        Si Robot 2 est libre → démarre immédiatement. Sinon → file d'attente.
        """
        if zone.name in self._in_queue:
            return
        if self.state == Robot2.IDLE:
            self._start_mission(zone)
        else:
            self._queue.append(zone)
            self._in_queue.add(zone.name)

    # ------------------------------------------------------------------
    # Update principal
    # ------------------------------------------------------------------
    def update(self, dt, robot1=None):
        """
        robot1 : référence au RobotMobile de Robot1 pour collision inter-robots.
        """
        if self.state == Robot2.IDLE:
            self.robot.commander(v=0.0, omega=0.0)
            self.vitesse = 0.0
            return

        tx, ty = self._current_target()
        self.controleur.set_target(tx, ty)

        # Rendre Robot 1 visible au Lidar de Robot 2
        if robot1 is not None:
            self.env.autres_robots = [(robot1.x, robot1.y, robot1.rayon)]
        else:
            self.env.autres_robots = []

        cmd = self.controleur.update(self.robot, self.env, dt)
        self.env.autres_robots = []

        self.robot.commander(**cmd)
        self._update_physics(dt, robot1)

        self.lidar_data = self.env.lidar_data
        self.vitesse    = abs(cmd.get("v", 0.0))

        self._check_transitions()

    # ------------------------------------------------------------------
    # 1) COLLISION INTER-ROBOTS
    # ------------------------------------------------------------------
    def _update_physics(self, dt, robot1=None):
        """
        Applique le mouvement et annule en cas de collision :
        bordures du monde, murs, ou contact avec Robot 1.
        """
        r         = self.robot.rayon
        old_x     = self.robot.x
        old_y     = self.robot.y
        old_theta = self.robot.orientation

        self.robot.mettre_a_jour(dt)

        # Limites du monde
        demi_L = self.env.largeur / 2
        demi_H = self.env.hauteur / 2
        out = (
            self.robot.x - r < -demi_L or self.robot.x + r > demi_L or
            self.robot.y - r < -demi_H or self.robot.y + r > demi_H
        )
        if out:
            self.robot.x, self.robot.y, self.robot.orientation = old_x, old_y, old_theta
            return

        # Collisions murs/obstacles
        for obs in self.env.obstacles:
            if hasattr(obs, "collision") and obs.collision((self.robot.x, self.robot.y), r):
                self.robot.x, self.robot.y, self.robot.orientation = old_x, old_y, old_theta
                return

        # Collision avec Robot 1
        if robot1 is not None:
            min_dist = r + robot1.rayon
            dx = self.robot.x - robot1.x
            dy = self.robot.y - robot1.y
            if (dx * dx + dy * dy) < min_dist * min_dist:
                self.robot.x, self.robot.y, self.robot.orientation = old_x, old_y, old_theta

    # ------------------------------------------------------------------
    # Cible FSM
    # ------------------------------------------------------------------
    def _current_target(self):
        """Retourne la position cible (x, y) selon l'état FSM actuel."""
        if self.state == Robot2.GO_ZONE:
            return self.target_zone.x, self.target_zone.y
        if self.state in (Robot2.GO_EXPORT, Robot2.DROP, Robot2.PICK):
            return self.export_zone.x, self.export_zone.y
        return self.robot.x, self.robot.y

    # ------------------------------------------------------------------
    # Transitions FSM
    # ------------------------------------------------------------------
    def _check_transitions(self):
        """Vérifie si le robot a atteint sa cible et fait avancer la FSM."""
        tx, ty = self._current_target()
        dist   = math.hypot(self.robot.x - tx, self.robot.y - ty)

        if self.state == Robot2.GO_ZONE and dist < ARRIVE_RADIUS:
            self.carry = self.target_zone.vider()
            self.state = Robot2.GO_EXPORT

        elif self.state == Robot2.GO_EXPORT and dist < ARRIVE_RADIUS:
            self.state = Robot2.DROP

        elif self.state == Robot2.DROP:
            self.export_zone.count += self.carry
            self.total_exported    += self.carry
            self.carry              = 0
            self.target_zone        = None

            if self._queue:
                nxt = self._queue.popleft()
                self._in_queue.discard(nxt.name)
                self._start_mission(nxt)
            else:
                self.state = Robot2.IDLE

    def _start_mission(self, zone):
        """Lance la navigation vers une zone de stockage à vider."""
        self.target_zone = zone
        self.state       = Robot2.GO_ZONE

    def __repr__(self):
        """Représentation textuelle pour le debug."""
        return f"Robot2(state={self.state}, carry={self.carry}, x={self.robot.x:.2f}, y={self.robot.y:.2f})"
