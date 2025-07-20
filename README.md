# Gescol - Application de Gestion Pédagogique

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1.4%2B-orange.svg)
![Flask-Login](https://img.shields.io/badge/Flask--Login-0.6%2B-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Description du Projet

Gescol est une application web de gestion pédagogique développée avec Flask, **spécifiquement conçue pour les professeurs d'informatique en Tunisie**. Elle permet aux utilisateurs de gérer leurs classes, leurs élèves et les notes associées de manière simple et intuitive. L'application inclut des fonctionnalités d'authentification pour garantir la séparation des données entre les différents utilisateurs.

## Fonctionnalités Clés

*   **Authentification Utilisateur :** Inscription, connexion et déconnexion sécurisées pour chaque utilisateur.
*   **Gestion des Classes :**
    *   Création, modification et suppression de classes (identifiant, niveau, section, numéro de laboratoire).
    *   Chaque classe est liée à l'utilisateur qui l'a créée.
*   **Gestion des Élèves :**
    *   Ajout, modification et suppression d'élèves (nom, prénom, numéro d'ordre).
    *   Association des élèves à une classe spécifique.
    *   Les élèves sont implicitement liés à l'utilisateur via leur classe.
*   **Gestion des Notes :**
    *   Saisie des notes pour chaque élève, avec spécification du type (Devoir de Contrôle - DC, Devoir de Synthèse - DS, Note de Contrôle Continu - NCC) et du trimestre.
    *   Les notes sont liées à l'élève, et donc à l'utilisateur.
*   **Calcul des Moyennes :**
    *   Calcul automatique des moyennes trimestrielles pour chaque élève.
    *   Les notes de type "Devoir de Synthèse" (DS) ont un coefficient de 2 dans le calcul de la moyenne.
*   **Tableau de Bord (Dashboard) :**
    *   Vue d'ensemble des statistiques globales (nombre total de classes et d'élèves) pour l'utilisateur connecté.
    *   Statistiques détaillées par classe, incluant le nombre d'élèves et la moyenne générale de la classe.
*   **Interface Utilisateur Moderne :** Interface conviviale avec CSS, barre de navigation et une page d'accueil informative.

## Technologies Utilisées

*   **Backend :**
    *   [Python](https://www.python.org/)
    *   [Flask](https://flask.palletsprojects.com/) (Framework web)
    *   [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) (ORM pour la base de données)
    *   [Flask-Login](https://flask-login.readthedocs.io/) (Gestion de l'authentification utilisateur)
    *   [Werkzeug](https://werkzeug.palletsprojects.com/) (Bibliothèque utilitaire pour WSGI)
    *   [SQLite](https://www.sqlite.org/index.html) (Base de données légère par défaut)
*   **Frontend :**
    *   HTML5
    *   CSS3
    *   JavaScript

## Installation et Lancement

Suivez ces étapes pour configurer et exécuter le projet localement :

### Prérequis

Assurez-vous d'avoir les éléments suivants installés sur votre système :

*   [Python 3.9+](https://www.python.org/downloads/)
*   [pip](https://pip.pypa.io/en/stable/installation/) (Gestionnaire de paquets Python)
*   [Git](https://git-scm.com/downloads)

### Étapes d'Installation

1.  **Cloner le dépôt :**
    ```bash
    git clone https://github.com/AmineMessaoudi/gescol-flask-app.git
    cd gescol-flask-app
    ```

2.  **Créer et activer un environnement virtuel :**
    Il est fortement recommandé d'utiliser un environnement virtuel pour isoler les dépendances du projet.

    ```bash
    python -m venv venv
    # Sur Windows
    venv\\Scripts\\activate
    # Sur macOS/Linux
    source venv/bin/activate
    ```

3.  **Installer les dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialiser la base de données :**
    La base de données SQLite (`gescol.db`) sera créée automatiquement au premier lancement de l'application si elle n'existe pas.

5.  **Lancer l'application :**
    ```bash
    flask run
    ```
    Si le port par défaut (5000) est déjà utilisé, vous pouvez spécifier un autre port :
    ```bash
    flask run --port=8000
    ```

    L'application sera accessible à l'adresse `http://127.0.0.1:5000/` (ou le port que vous avez spécifié).

## Utilisation

1.  **Inscription et Connexion :** Accédez aux pages `/register` et `/login` pour créer un compte et vous connecter.
2.  **Navigation :** Utilisez la barre de navigation pour accéder aux différentes sections (Classes, Élèves, Dashboard).
3.  **Gestion des Données :** Créez, modifiez et supprimez vos classes, élèves et notes. Toutes les données que vous saisissez sont isolées et ne sont visibles que par votre compte.

## Structure du Projet

```
gescol/
├── .gitignore
├── app.py                  # Fichier principal de l'application Flask
├── requirements.txt        # Liste des dépendances Python
├── instance/               # Contient la base de données SQLite (gescol.db)
├── static/
│   ├── script.js           # Fichiers JavaScript
│   └── style.css           # Fichiers CSS pour le style de l'application
└── templates/              # Fichiers HTML (templates Jinja2)
    ├── base.html           # Template de base pour toutes les pages
    ├── classes.html        # Page de gestion des classes
    ├── dashboard.html      # Tableau de bord avec statistiques
    ├── details_eleve.html  # Détails et notes d'un élève
    ├── eleves.html         # Page de gestion des élèves
    ├── index.html          # Page d'accueil
    ├── login.html          # Page de connexion
    ├── modifier_classe.html# Page de modification d'une classe
    ├── modifier_eleve.html # Page de modification d'un élève
    ├── modifier_note.html  # Page de modification d'une note
    └── register.html       # Page d'inscription
```

## Améliorations Futures (TODO)

Voici quelques pistes d'amélioration et de nouvelles fonctionnalités envisagées pour le projet Gescol :

*   **Gestion des Matières/Cours :** Ajouter la possibilité de définir différentes matières et d'y associer les notes.
*   **Validation des Formulaires Côté Client :** Implémenter des validations JavaScript pour une meilleure expérience utilisateur.
*   **Design Responsive :** Optimiser l'interface pour une compatibilité totale avec les appareils mobiles et tablettes.
*   **Tests Unitaires et d'Intégration :** Développer une suite de tests pour assurer la robustesse et la maintenabilité du code.
*   **Conteneurisation (Docker) :** Fournir une configuration Docker pour faciliter le déploiement de l'application.
*   **Localisation (i18n) :** Ajouter la prise en charge de plusieurs langues (arabe, français) pour l'interface utilisateur.

## Contribution

Les contributions sont les bienvenues ! Si vous souhaitez améliorer ce projet, n'hésitez pas à soumettre des "issues" ou des "pull requests".

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Contact

**Auteur :** Amine Messaoudi
**Email :** [amine.messaoudi.info@gmail.com](mailto:amine.messaoudi.info@gmail.com)
**GitHub :** [AmineMessaoudi/gescol-flask-app](https://github.com/AmineMessaoudi/gescol-flask-app)

