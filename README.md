# POO & Robotique Mobile — Projet Fil Rouge

**Master Data & IA (FGES)**  
**Contributeurs :** Ouail LEKHCHINE & Amani YAHIA BEY  
**Supervisé par :** M. GOUGUET

---

## Présentation

Ce dépôt correspond au projet du module **Programmation Orientée Objet et Robotique Mobile**.

L'objectif est de construire progressivement une **simulation 2D de robots mobiles autonomes** en Python en appliquant les principes de la POO (encapsulation, héritage, polymorphisme, classes abstraites) et une architecture **MVC**.

Le projet aboutit à une simulation complète avec deux robots autonomes, un capteur Lidar, une gestion de batterie, un convoyeur de colis et un évitement d'obstacles multi-modes.

---

## Lancer la simulation

```bash
pip install pygame
python project/main.py
```

**Touches clavier :**

| Touche | Action |
|--------|--------|
| `H` | Afficher / masquer les rayons Lidar |
| `P` | Pause / reprise |
| Fermer la fenêtre | Quitter |

---

## Scénario

Le monde fait **10 m × 10 m** et contient un convoyeur, deux zones de stockage, une zone d'export et une zone de recharge.

**Robot 1** collecte les colis sur le convoyeur et les trie par couleur (rouge / vert) dans les zones de stockage. Sa batterie se consomme à chaque livraison (−25 %) et se recharge automatiquement quand le niveau atteint ≤ 25 %.

**Robot 2** surveille les zones de stockage et les vide vers la zone d'export dès qu'elles sont pleines.

Les deux robots naviguent de façon autonome et s'évitent mutuellement grâce à leur capteur Lidar.

---

## Architecture

Le code suit un pattern **MVC**. Tout le code source est dans le package `project/robot/` ; `project/main.py` est le point d'entrée.

### Hiérarchie des classes principales

```
Moteur (ABC)
├── MoteurDifferentiel        ← utilisé (v, ω)
└── MoteurOmnidirectionnel    ← non utilisé (vx, vy, ω)

Capteur (ABC)
└── Lidar                     ← 41 rayons, FOV 220°, portée 4 m

Obstacle (ABC)
├── ObstacleRectangle         ← murs internes et bordures
└── ObstacleCercle

Controleur (ABC)
├── ControleurTerminal
└── ControleurClavierPygame

RobotMobile                   ← attributs privés + @property
Robot2
  ├── RobotMobile
  ├── Lidar
  └── ControleurAuto

Environnement                 ← état du monde + physique + rollback collisions
VuePygame                     ← rendu Pygame + HUD
```

### Évitement d'obstacles (`ControleurAuto`)

Le Lidar alimente une machine à états à 5 modes (normal → ralentissement → évitement → danger → backup / escape) avec détection de blocage au bout de 1,5 s.

### FSM Robot 1 — Batterie

`R1_WORKING` ↔ `R1_CHARGING` : déclenché à ≤ 25 %, recharge sur zone CHARGE jusqu'à 100 %.

### FSM Robot 2

`IDLE → GO_ZONE → PICK → GO_EXPORT → DROP → IDLE`

---

## Diagramme UML

![Diagramme de classes](../project/uml/class_diag.png)

Source PlantUML : `project/uml/class_diag.puml`

---

## Structure du projet

```
project/
├── main.py                  ← point d'entrée, boucle de jeu, FSM Robot 1
├── robot/
│   ├── robot_mobile.py      ← classe de base robot
│   ├── moteur.py            ← moteurs (différentiel, omnidirectionnel)
│   ├── environnement.py     ← monde, physique, collisions
│   ├── controleur_auto.py   ← navigation autonome + évitement Lidar
│   ├── lidar.py             ← capteur 2D ray-cast
│   ├── robot2.py            ← robot videur (FSM autonome)
│   ├── vue.py               ← rendu Pygame
│   ├── Zone.py              ← zones de stockage / export / charge
│   ├── Colis.py             ← colis (WAITING → CARRIED → DELIVERED)
│   ├── batterie.py          ← modèle de batterie
│   ├── file_attente.py      ← convoyeur FIFO avec warmup
│   ├── ObstacleRectangle.py ← mur rectangulaire + intersection Lidar
│   ├── obstacle.py          ← interface Obstacle (ABC)
│   ├── planner_astar.py     ← A* sur grille (non intégré)
│   └── path_follower.py     ← suivi de waypoints (non intégré)
├── assets/                  ← sprites robot et convoyeur
└── uml/
    ├── class_diag.puml      ← source PlantUML
    └── class_diag.png       ← diagramme généré
```

---

## Objectifs pédagogiques couverts

| Concept | Où |
|---|---|
| Encapsulation (attributs privés + properties) | `RobotMobile` |
| Héritage | `MoteurDifferentiel`, `Lidar`, `ObstacleCercle` |
| Polymorphisme | `Obstacle.collision()`, `Moteur.mettre_a_jour()` |
| Classes abstraites (ABC) | `Moteur`, `Capteur`, `Obstacle`, `Controleur` |
| Méthodes statiques & classmethod | `RobotMobile.moteur_valide()`, `nombre_robots()` |
| Architecture MVC | `Environnement` / `ControleurAuto` / `VuePygame` |
| Machine à états (FSM) | Robot 1 (batterie + mission), Robot 2, ControleurAuto |
| Capteur simulé | `Lidar` (ray-cast AABB + cercle) |
| Pathfinding | `GridPlannerAStar` (A*) |

---

## Auteurs

Ouail LEKHCHINE — Amani YAHIA BEY
