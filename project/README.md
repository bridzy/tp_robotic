# tp_robotic
# TP1 — Prise en main de la POO (Robotique Mobile)

Ce projet correspond au **TP1 : prise en main de la Programmation Orientée Objet (POO)** appliquée à un cas simple de **robot mobile**.  
L’objectif est de construire une base logicielle claire (classes, encapsulation, héritage, polymorphisme) et de préparer la suite du **projet fil rouge** (simulation/navigation).

---

## Objectifs pédagogiques

- Implémenter une **classe `RobotMobile`** (position + orientation) et ses méthodes de mouvement.
- Mettre en place l’**encapsulation** avec attributs privés + propriétés (getters/setters).
- Introduire une architecture extensible via un **moteur abstrait** (`Moteur`) et deux implémentations :
  - `MoteurDifferentiel` (v, ω)
  - `MoteurOmnidirectionnel` (vx, vy, ω)
- Documenter l’architecture avec un **diagramme UML** (PlantUML).
- Structurer le code comme un mini-projet Python (organisation, README, Git).

---

## Fonctionnalités

### 1) RobotMobile
- Attributs : position **(x, y)**, orientation **θ** (radians)
- Méthodes :
  - `avancer(distance)` : déplacement selon l’orientation
  - `tourner(angle)` : rotation modulo 2π
  - `afficher()` / `__str__()` : affichage lisible

### 2) Moteurs (architecture orientée objet)
- **Classe abstraite** `Moteur` :
  - `commander(**kwargs)`
  - `mettre_a_jour(robot, dt)`
- **MoteurDifferentiel** :
  - commande : `v`, `omega`
  - intégration temporelle (dt)
- **MoteurOmnidirectionnel** :
  - commande : `vx`, `vy`, `omega`
  - mouvement relatif à l’orientation

### 3) Outils POO supplémentaires
- Compteur d’instances : `RobotMobile._nb_robots` + `RobotMobile.nombre_robots()`
- Validation moteur : `RobotMobile.moteur_valide(moteur)` (statique)

---

## Structure du projet

