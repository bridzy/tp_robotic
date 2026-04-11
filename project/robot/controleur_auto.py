import math


class ControleurAuto:
    """
    Contrôleur autonome amélioré :
    - go-to-goal + évitement lidar vectoriel
    - ralentissement progressif près des murs
    - MODE BACKUP  : marche arrière si vraiment bloqué contre un mur
    - MODE ESCAPE  : rotation sur place si coincé en coin (détection blocage)
    - Détection de blocage : si le robot n'avance pas pendant N ticks → escape
    """

    def __init__(self, lidar):
        """
        Paramètre :
            lidar : instance de Lidar — fournit les distances à chaque tick
        """
        self.lidar  = lidar
        self.target = None

        # Commandes lissées
        self.v_cmd = 0.0
        self.w_cmd = 0.0

        # Paramètres généraux
        self.v_max       = 0.50
        self.v_min       = 0.12
        self.v_near_wall = 0.20
        self.v_turn      = 0.18

        self.omega_max = 0.90
        self.alpha_v   = 0.25
        self.alpha_w   = 0.25

        # Seuils obstacle (en mètres)
        self.front_slow   = 0.85
        self.front_avoid  = 0.55
        self.front_danger = 0.35   # légèrement augmenté pour réagir plus tôt
        self.front_backup = 0.22   # seuil marche arrière

        # Seuils latéraux
        self.side_near = 0.45

        # Évitement
        self.k_goal  = 1.0
        self.k_avoid = 1.20

        # ── Détection de blocage ──────────────────────────────────────
        self._stuck_timer    = 0.0
        self._stuck_threshold = 1.5    # secondes sans mouvement → escape
        self._last_x         = None
        self._last_y         = None
        self._min_displacement = 0.03  # déplacement minimum par tick pour ne pas être "bloqué"

        # ── Mode BACKUP ───────────────────────────────────────────────
        self._backup_timer   = 0.0
        self._backup_duration = 0.8    # durée marche arrière (secondes)
        self._in_backup      = False

        # ── Mode ESCAPE (rotation sur place) ─────────────────────────
        self._escape_timer   = 0.0
        self._escape_duration = 1.2    # durée rotation d'échappement
        self._escape_dir     = 1.0     # +1 ou -1
        self._in_escape      = False

        # ── Direction de virage mémorisée (évite oscillation en coin) ─
        self._last_turn_dir  = 1.0     # +1 = gauche, -1 = droite

    # ------------------------------------------------------------------
    # Méthodes utilitaires statiques (privées)
    # ------------------------------------------------------------------
    @staticmethod
    def _clamp(x, lo, hi):
        """Borne x entre lo et hi."""
        return lo if x < lo else hi if x > hi else x

    @staticmethod
    def _wrap_pi(a):
        """Ramène un angle dans ]-π, π]."""
        return (a + math.pi) % (2 * math.pi) - math.pi


    def set_target(self, x, y):
        """Définit la cible à atteindre (mètres). Réinitialise le suivi de position si la cible change."""
        new_target = (float(x), float(y))
        if self.target != new_target:
            self._last_x = None
            self._last_y = None
        self.target = new_target

    def update(self, robot, env, dt):
        """
        Calcule et retourne la commande {v, omega} pour ce tick.
        Séquence : Lidar → détection blocage → ESCAPE → BACKUP
        → marche arrière immédiate → go-to-goal + évitement.
        """
        if self.target is None:
            return {"v": 0.0, "omega": 0.0}

        # ── Lecture lidar ─────────────────────────────────────────────
        lidar_data   = self.lidar.read(env, robot)
        env.lidar_data = lidar_data

        dists  = lidar_data["distances"]
        angles = self.lidar._angles()
        n      = len(dists)
        mid    = n // 2

        front     = min(dists[max(0, mid - 2):min(n, mid + 3)])
        left_min  = min(dists[:n // 3])
        right_min = min(dists[-n // 3:])
        # ── Détection de blocage ──────────────────────────────────────
        if self._last_x is not None:
            displacement = math.hypot(robot.x - self._last_x, robot.y - self._last_y)
            if displacement < self._min_displacement and front < self.front_avoid:
                self._stuck_timer += dt
            else:
                self._stuck_timer = max(0.0, self._stuck_timer - dt * 0.5)
        self._last_x, self._last_y = robot.x, robot.y

        # Déclencher ESCAPE si bloqué trop longtemps
        if self._stuck_timer >= self._stuck_threshold and not self._in_escape and not self._in_backup:
            self._in_escape    = True
            self._escape_timer = 0.0
            self._escape_dir   = 1.0 if left_min > right_min else -1.0
            self._stuck_timer  = 0.0

        # ── MODE ESCAPE : rotation sur place pour se dégager ─────────
        if self._in_escape:
            self._escape_timer += dt
            if self._escape_timer < self._escape_duration:
                w_esc = self._escape_dir * self.omega_max * 1.1
                self.v_cmd = (1 - self.alpha_v) * self.v_cmd  # freiner
                self.w_cmd = (1 - self.alpha_w) * self.w_cmd + self.alpha_w * w_esc
                return {"v": float(self.v_cmd), "omega": float(self.w_cmd)}
            else:
                self._in_escape = False
                # Enchaîner avec BACKUP pour s'écarter du mur
                self._in_backup    = True
                self._backup_timer = 0.0

        # ── MODE BACKUP : marche arrière courte ───────────────────────
        if self._in_backup:
            self._backup_timer += dt
            if self._backup_timer < self._backup_duration:
                # Reculer doucement, garder un peu de rotation vers la cible
                self.v_cmd = (1 - self.alpha_v) * self.v_cmd + self.alpha_v * (-0.20)
                self.w_cmd = (1 - self.alpha_w) * self.w_cmd
                return {"v": float(self.v_cmd), "omega": float(self.w_cmd)}
            else:
                self._in_backup   = False
                self._stuck_timer = 0.0

        # ── Marche arrière immédiate si trop proche d'un mur ─────────
        if front < self.front_backup:
            if abs(left_min - right_min) > 0.05:
                self._last_turn_dir = 1.0 if left_min > right_min else -1.0
            self.v_cmd = (1 - self.alpha_v) * self.v_cmd + self.alpha_v * (-0.15)
            self.w_cmd = (1 - self.alpha_w) * self.w_cmd + self.alpha_w * (self._last_turn_dir * self.omega_max)
            return {"v": float(self.v_cmd), "omega": float(self.w_cmd)}

        # ── Direction vers la cible ───────────────────────────────────
        tx, ty     = self.target
        dx         = tx - robot.x
        dy         = ty - robot.y
        dist_goal   = math.hypot(dx, dy)
        near_target = dist_goal < 0.65   # proche de la cible : atténuer l'évitement

        if dist_goal < 0.20:
            self.v_cmd = (1 - self.alpha_v) * self.v_cmd
            self.w_cmd = (1 - self.alpha_w) * self.w_cmd
            return {"v": float(self.v_cmd), "omega": float(self.w_cmd)}

        goal_x = dx / (dist_goal + 1e-9)
        goal_y = dy / (dist_goal + 1e-9)

        # ── Vecteur d'évitement lidar ─────────────────────────────────
        avoid_x = avoid_y = 0.0
        for dist, ang in zip(dists, angles):
            if abs(ang) > math.radians(110):
                continue
            if dist < 1.2:
                strength    = (1.2 - dist) / 1.2
                weight      = max(0.20, math.cos(ang))
                world_angle = robot.orientation + ang
                avoid_x    -= math.cos(world_angle) * strength * weight
                avoid_y    -= math.sin(world_angle) * strength * weight

        # ── Biais de virage si obstacle devant ───────────────────────
        side_turn_bias = 0.0
        if front < self.front_avoid and not near_target:
            side_turn_bias = +0.55 if left_min > right_min else -0.55

        # ── Combinaison goal + avoidance ──────────────────────────────
        # Réduire l'évitement quadratiquement quand on approche la cible
        k_avoid_eff = self.k_avoid * (dist_goal / 0.65) ** 2 if near_target else self.k_avoid
        final_x = self.k_goal * goal_x + k_avoid_eff * avoid_x
        final_y = self.k_goal * goal_y + k_avoid_eff * avoid_y

        desired_angle = math.atan2(final_y, final_x)
        if abs(side_turn_bias) > 0.0:
            desired_angle += side_turn_bias

        err     = ControleurAuto._wrap_pi(desired_angle - robot.orientation)
        abs_err = abs(err)

        # ── Rotation ─────────────────────────────────────────────────
        w_des = ControleurAuto._clamp(1.40 * err, -self.omega_max, self.omega_max)

        # Si bloqué devant → rotation franche (supprimé si déjà proche de la cible)
        if front < self.front_danger and not near_target:
            if abs(left_min - right_min) > 0.05:
                self._last_turn_dir = 1.0 if left_min > right_min else -1.0
            w_des = self._last_turn_dir * self.omega_max * 1.1

        # ── Vitesse linéaire ──────────────────────────────────────────
        v_des = self.v_max

        # Freinage selon distance à la cible
        if dist_goal < 0.80: v_des = min(v_des, 0.35)
        if dist_goal < 0.35: v_des = min(v_des, 0.20)

        # Freinage selon murs latéraux
        if left_min < self.side_near or right_min < self.side_near:
            v_des = min(v_des, self.v_near_wall)

        # Freinage selon obstacle devant
        if front < self.front_slow:   v_des = min(v_des, 0.26)
        if front < self.front_avoid:  v_des = min(v_des, 0.16)
        if front < self.front_danger: v_des = 0.08

        # Freinage selon angle à corriger
        if abs_err > math.radians(25): v_des = min(v_des, 0.20)
        if abs_err > math.radians(50): v_des = min(v_des, self.v_turn)

        # Vitesse minimum (évite spin pur)
        if front > self.front_danger:
            v_des = max(self.v_min, v_des)

        # ── Lissage ───────────────────────────────────────────────────
        self.v_cmd = (1 - self.alpha_v) * self.v_cmd + self.alpha_v * v_des
        self.w_cmd = (1 - self.alpha_w) * self.w_cmd + self.alpha_w * w_des

        return {"v": float(self.v_cmd), "omega": float(self.w_cmd)}
