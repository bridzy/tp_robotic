class Environnement:
    """
    Modèle du monde : contient le robot, les obstacles et les zones.

    Responsabilités :
        - Stocker les éléments du monde (robot, obstacles, zones)
        - Appliquer la physique à chaque tick : mouvement + collisions
        - Centraliser tous les attributs d'état de la simulation

    Attributs déclarés ici et utilisés par main.py et vue.py :
        Physique    → robot, obstacles, zones, largeur, hauteur
        Mission R1  → file_attente, colis_transporte, nb_livres, home
        Capteur     → lidar_sensor, lidar_data
        Simulation  → paused, robot2, batterie
        FSM R1      → _r1_state, _r1_vitesse
    """

    def __init__(self, largeur=10.0, hauteur=10.0):
        # ── Dimensions du monde ────────────────────────────────────
        self.largeur = float(largeur)
        self.hauteur = float(hauteur)

        # ── Éléments physiques ─────────────────────────────────────
        self.robot     = None
        self.obstacles = []   # obstacles bloquants (collision physique)
        self.zones     = []   # zones non bloquantes (stockage, export, charge)

        # ── Mission Robot 1 ────────────────────────────────────────
        self.file_attente      = None   # convoyeur de colis (FileAttenteColis)
        self.colis_transporte  = None   # colis actuellement porté par Robot 1
        self.nb_livres         = 0      # compteur total de livraisons réussies
        self.home              = (0.0, 0.0)  # position de repos de Robot 1

        # ── Capteur Lidar (référence pour la vue) ──────────────────
        self.lidar_sensor = None   # instance Lidar de Robot 1
        self.lidar_data   = None   # dernières distances lues (dict)

        # ── État de la simulation ──────────────────────────────────
        self.paused   = False   # True = simulation gelée (touche P)
        self.robot2   = None    # référence à Robot 2 (pour la vue)
        self.batterie = None    # batterie de Robot 1 (pour la vue)

        # ── FSM batterie Robot 1 ───────────────────────────────────
        self._r1_state   = "WORKING"  # état courant : WORKING ou CHARGING
        self._r1_vitesse = 0.0        # vitesse instantanée (m/s) pour le HUD

    # ------------------------------------------------------------------
    # Ajout d'éléments
    # ------------------------------------------------------------------
    def ajouter_robot(self, robot):
        self.robot = robot

    def ajouter_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def ajouter_zone(self, zone):
        self.zones.append(zone)

    # ------------------------------------------------------------------
    # Mise à jour physique (appelée chaque tick)
    # ------------------------------------------------------------------
    def mettre_a_jour(self, dt):
        """
        Déplace le robot via son moteur puis annule le mouvement
        si une collision est détectée :
          1) sortie des limites du monde
          2) contact avec un obstacle (polymorphisme via collision())
        """
        if self.robot is None:
            return

        # Sauvegarde avant mouvement (pour rollback en cas de collision)
        old_x     = self.robot.x
        old_y     = self.robot.y
        old_theta = self.robot.orientation

        self.robot.mettre_a_jour(dt)

        r = getattr(self.robot, "rayon", 0.25)

        # 1) Limites du monde
        demi_L = self.largeur / 2
        demi_H = self.hauteur / 2
        hors_limites = (
            self.robot.x - r < -demi_L or self.robot.x + r > demi_L or
            self.robot.y - r < -demi_H or self.robot.y + r > demi_H
        )
        if hors_limites:
            self.robot.x           = old_x
            self.robot.y           = old_y
            self.robot.orientation = old_theta
            return

        # 2) Collisions obstacles (polymorphisme)
        for obs in self.obstacles:
            if hasattr(obs, "collision") and obs.collision((self.robot.x, self.robot.y), r):
                self.robot.x           = old_x
                self.robot.y           = old_y
                self.robot.orientation = old_theta
                return

        # 3) Collision avec Robot 2
        if self.robot2 is not None and hasattr(self.robot2, 'robot'):
            r2 = self.robot2.robot
            min_dist = r + getattr(r2, 'rayon', 0.22)
            dx = self.robot.x - r2.x
            dy = self.robot.y - r2.y
            if (dx * dx + dy * dy) < min_dist * min_dist:
                self.robot.x           = old_x
                self.robot.y           = old_y
                self.robot.orientation = old_theta
