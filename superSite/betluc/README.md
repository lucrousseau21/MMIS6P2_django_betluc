# BetLuc - Application de Paris Sportifs

BetLuc est une application web de paris sportifs permettant aux utilisateurs de parier sur des matchs de football.

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Un environnement virtuel Python (recommandé)

## Installation

1. Clonez le dépôt :
```bash
git clone [URL_DU_REPO]
cd betluc
```

2. Créez et activez un environnement virtuel :
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurez la base de données :
```bash
python manage.py migrate
```

5. Initialisez les données :
```bash
python setup.py
```

Cette commande va :
- Charger les équipes et les journées initiales
- Générer 30 journées de matchs
- Créer 30 utilisateurs avec des paris aléatoires

## Démarrage

1. Lancez le serveur de développement :
```bash
python manage.py runserver
```

2. Accédez à l'application dans votre navigateur :
```
http://127.0.0.1:8000
```

## Fonctionnalités

- Inscription et connexion des utilisateurs
- Consultation des matchs et des cotes
- Placement de paris
- Suivi des paris en cours et de l'historique
- Dépôt et retrait d'argent
- Classement des parieurs
- Avancement automatique des matchs

## Configuration

- Les matchs sont générés automatiquement pour 30 journées
- Chaque journée contient 5 matchs
- Les utilisateurs sont créés avec :
  - Des noms d'utilisateur aléatoires (combinaison de prénoms et noms français)
  - Des adresses email au format `username@gmail.com`
  - Le mot de passe `azerty` pour tous les utilisateurs
  - Des soldes initiaux entre 100€ et 1000€
  - Entre 5 et 15 paris aléatoires par utilisateur

## Maintenance

Pour mettre à jour l'état des matchs :
```bash
python manage.py update_match_statuses
```

Pour mettre à jour un match spécifique :
```bash
python manage.py update_specific_match [ID_DU_MATCH]
```

## Support

Pour toute question ou problème, veuillez ouvrir une issue sur le dépôt GitHub. 