# POO & Robotique Mobile — TP / Projet Fil Rouge

**Master Data & IA (FGES)**  
**Contributeurs :** Ouail LEKHCHINE & Amani YAHIA BEY  
**Supervisé par :** M. GOUGUET

---

## Présentation

Ce dépôt correspond au projet du module **Programmation Orientée Objet et Robotique Mobile**.

L’objectif est de construire progressivement une **simulation de robot mobile** en Python en appliquant :

- les principes de la **Programmation Orientée Objet (POO)** :
  - classes
  - encapsulation
  - héritage
  - polymorphisme
- une architecture **MVC (Model - View - Controller)**
- une simulation interactive (terminal puis graphique avec Pygame)

---

## Contenu actuel

### TP1 — Prise en main POO

- Classe `RobotMobile`
- Encapsulation (properties)
- Moteurs :
  - `MoteurDifferentiel`
  - `MoteurOmnidirectionnel`
- Méthodes statiques et classmethod
- Diagramme UML (PlantUML)

### TP2 — Architecture MVC & Simulation

- Architecture MVC :
  - Modèle (Robot, Moteur)
  - Vue (Terminal + Pygame)
  - Contrôleur (Terminal + Clavier)
- Simulation graphique avec **Pygame**
- Environnement :
  - gestion des obstacles
  - collisions
  - rollback du mouvement

---

## Fonctionnalités principales

### RobotMobile

- Position `(x, y)`
- Orientation `θ` (radians)
- Rayon (collision)
- Déplacement :
  - avancer(distance)
  - tourner(angle)

### Moteurs

Classe abstraite :

- `commander(**kwargs)`
- `mettre_a_jour(robot, dt)`

Implémentations :

- Moteur différentiel (v, omega)
- Moteur omnidirectionnel (vx, vy, omega)

### Environnement

- Contient robot + obstacles
- Détecte collisions
- Annule mouvement si collision

### Vue Pygame

- Conversion mètres → pixels
- Affichage robot + orientation
- Affichage obstacles

---

## Structure du projet

```

project/
robot/
robot_mobile.py
moteur.py
controleur.py
vue.py
environnement.py
obstacle.py
obstacle_cercle.py
docs/
uml/
class_diagram.puml
class_diagram.svg
main.py
README.md

````

---

## Installation

Python 3.10+

Installer pygame :

```bash
pip install pygame
````

---

## Lancer la simulation

```bash
python main.py
```

---

## Contrôles clavier (Pygame)

* Flèche HAUT / BAS → vitesse linéaire
* Flèche GAUCHE / DROITE → rotation

Fermer la fenêtre pour arrêter la simulation.

---

## UML

Diagramme UML généré avec PlantUML :

```
docs/uml/class_diagram.puml
```

---

## Objectifs pédagogiques

* Architecture propre MVC
* Code modulaire extensible
* Simulation robotique simple
* Travail collaboratif via Git

---

## Auteurs

Ouail LEKHCHINE
Amani YAHIA BEY
