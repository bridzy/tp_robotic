import random
from robot.Colis import Colis


class FileAttenteColis:
    """
    File FIFO de colis sur le convoyeur.
    - Phase warmup : spawn rapide (warmup_count colis au départ, délai court)
    - Phase normale : spawn aléatoire entre spawn_min_s et spawn_max_s
    """
    def __init__(
        self,
        center_x, center_y,
        width, height,
        spawn_min_s=8.0,
        spawn_max_s=18.0,
        max_size=6,
        spacing=0.34,
        warmup_count=3,       # colis pré-spawnés au démarrage
        warmup_delay=2.0      # délai entre chaque colis pendant le warmup
    ):
        self.center_x = float(center_x)
        self.center_y = float(center_y)
        self.width    = float(width)
        self.height   = float(height)

        self.spawn_min_s = float(spawn_min_s)
        self.spawn_max_s = float(spawn_max_s)
        self.max_size    = int(max_size)
        self.spacing     = float(spacing)

        self.colis       = []
        self.spawn_timer = 0.0

        # Warmup : spawn accéléré au début
        self._warmup_remaining = int(warmup_count)
        self._warmup_delay     = float(warmup_delay)
        self._in_warmup        = (warmup_count > 0)

        # Premier délai : warmup ou normal
        if self._in_warmup:
            self.next_spawn_delay = self._warmup_delay
        else:
            self.next_spawn_delay = random.uniform(self.spawn_min_s, self.spawn_max_s)

    # ------------------------------------------------------------------
    # Propriétés
    # ------------------------------------------------------------------
    @property
    def rect_world(self):
        """Rectangle du convoyeur sous forme (cx, cy, w, h) pour la vue."""
        return (self.center_x, self.center_y, self.width, self.height)

    def pickup_point(self):
        """Point de prise des colis : centre du convoyeur."""
        return self.center_x, self.center_y

    def has_waiting(self):
        """True s'il y a au moins un colis sur le convoyeur."""
        return len(self.colis) > 0

    def count(self):
        """Nombre de colis actuellement sur le convoyeur."""
        return len(self.colis)

    # ------------------------------------------------------------------
    # Update & spawn
    # ------------------------------------------------------------------
    def update(self, dt):
        """Avance le timer et spawne un colis si le délai est écoulé."""
        self.spawn_timer += float(dt)
        if self.spawn_timer >= self.next_spawn_delay:
            self.spawn_timer -= self.next_spawn_delay
            self._spawn_random()

            # Gérer la fin du warmup
            if self._in_warmup:
                self._warmup_remaining -= 1
                if self._warmup_remaining <= 0:
                    self._in_warmup = False
                    self.next_spawn_delay = random.uniform(self.spawn_min_s, self.spawn_max_s)
                else:
                    self.next_spawn_delay = self._warmup_delay
            else:
                self.next_spawn_delay = random.uniform(self.spawn_min_s, self.spawn_max_s)

    def _spawn_random(self):
        """Crée un colis de couleur aléatoire si le convoyeur n'est pas plein."""
        if len(self.colis) >= self.max_size:
            return
        couleur = random.choice(["RED", "GREEN"])
        self.colis.append(Colis(0.0, 0.0, couleur))
        self._relayout()

    def _relayout(self):
        """Replace tous les colis en file horizontale sur le convoyeur."""
        start_x = self.center_x - self.width / 2 + 0.35
        y = self.center_y
        for i, c in enumerate(self.colis):
            c.set_position(start_x + i * self.spacing, y)
            c.etat = Colis.WAITING

    # ------------------------------------------------------------------
    # Prise de colis
    # ------------------------------------------------------------------
    def try_pick_first(self, robot_x, robot_y, pick_radius):
        """
        Le robot prend le premier colis si il est dans le rayon de pickup.
        Retourne le Colis pris, ou None si trop loin ou file vide.
        """
        if not self.colis:
            return None
        px, py = self.pickup_point()
        if (robot_x - px) ** 2 + (robot_y - py) ** 2 > pick_radius * pick_radius:
            return None
        colis = self.colis.pop(0)
        colis.etat = Colis.CARRIED
        colis.set_position(robot_x, robot_y)
        self._relayout()
        return colis

    # ------------------------------------------------------------------
    # Info pour HUD
    # ------------------------------------------------------------------
    def time_until_next(self):
        """Temps restant avant le prochain spawn (en secondes)."""
        remaining = self.next_spawn_delay - self.spawn_timer
        return max(0.0, remaining)
