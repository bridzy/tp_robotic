"""
batterie.py — Modèle de batterie pour les robots.

Gère le niveau de charge (0–100%), la consommation par livraison
et la recharge progressive sur la zone CHARGE.
"""

CHARGE_RATE     = 10.0   # % rechargés par seconde sur la zone de charge
CHARGE_SEUIL    = 25.0   # % en dessous duquel le robot décide d'aller charger
CONSO_PAR_COLIS = 25.0   # % consommés à chaque livraison réussie


class Batterie:
    """
    Batterie d'un robot : niveau entre 0 et 100 %.

    Cycle de vie :
        100% → consommer() à chaque livraison → ≤25% → charger() sur zone CHARGE → 100%
    """

    def __init__(self, niveau_initial=100.0):
        """Initialise la batterie au niveau donné (défaut : pleine à 100%)."""
        self.niveau = float(niveau_initial)

    def consommer(self, quantite=CONSO_PAR_COLIS):
        """
        Retire `quantite` % de la batterie (défaut : CONSO_PAR_COLIS = 25%).
        Retourne True si la batterie est encore chargée, False si vide.
        """
        self.niveau = max(0.0, self.niveau - float(quantite))
        return self.niveau > 0.0

    def charger(self, dt):
        """
        Recharge progressive : ajoute CHARGE_RATE * dt %.
        Retourne True quand la batterie est pleine (100%).
        Appelée chaque tick tant que le robot est sur la zone CHARGE.
        """
        self.niveau = min(100.0, self.niveau + CHARGE_RATE * float(dt))
        return self.is_full()

    def needs_charge(self):
        """True si le niveau est inférieur ou égal au seuil d'alerte (25%)."""
        return self.niveau <= CHARGE_SEUIL

    def is_full(self):
        """True si la batterie est complètement chargée (100%)."""
        return self.niveau >= 100.0

    def pct(self):
        """Niveau arrondi en entier pour affichage dans le HUD."""
        return int(self.niveau)

    def color(self):
        """
        Couleur RGB selon le niveau, pour la barre de batterie dans le HUD :
            > 50% → vert
            > 25% → orange
            ≤ 25% → rouge (seuil d'alerte)
        """
        if self.niveau > 50:
            return (60, 200, 60)
        elif self.niveau > 25:
            return (230, 160, 0)
        else:
            return (220, 40, 40)

    def __repr__(self):
        """Représentation textuelle pour le debug."""
        return f"Batterie({self.niveau:.1f}%)"
