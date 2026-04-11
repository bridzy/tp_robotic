class Colis:
    """
    Représente un colis dans la simulation.

    Attributs :
        x, y    : position dans le monde (mètres)
        couleur : 'RED' ou 'GREEN' — détermine la zone de dépôt cible
        etat    : cycle de vie du colis (utiliser les constantes de classe)

    Constantes d'état :
        Colis.WAITING   → sur le convoyeur, en attente d'être pris
        Colis.CARRIED   → transporté par Robot 1
        Colis.DELIVERED → déposé dans la bonne zone de stockage
    """

    # Constantes d'état — utiliser ces constantes plutôt que des strings bruts
    # pour éviter les fautes de frappe et faciliter la maintenance
    WAITING   = "WAITING"
    CARRIED   = "CARRIED"
    DELIVERED = "DELIVERED"

    def __init__(self, x, y, couleur):
        """Crée un colis en position (x, y) avec la couleur donnée ('RED' ou 'GREEN')."""
        self.x       = float(x)
        self.y       = float(y)
        self.couleur = str(couleur).upper()   # normalisé : toujours en majuscules
        self.etat    = Colis.WAITING          # état initial : attend sur le convoyeur

    def set_position(self, x, y):
        """Déplace le colis (utilisé quand il est transporté par le robot)."""
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        """Représentation textuelle pour le debug."""
        return f"Colis({self.couleur}, etat={self.etat}, x={self.x:.2f}, y={self.y:.2f})"
