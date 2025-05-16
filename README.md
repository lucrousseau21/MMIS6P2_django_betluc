# BetLuc - Application de Paris Sportifs

Application web de paris sportifs développée avec Django, permettant aux utilisateurs de parier sur des matchs de football.

## Fonctionnalités

- Gestion des équipes et des ligues
- Système de paris sportifs
- Gestion des cotes en temps réel
- Interface utilisateur intuitive
- Système d'authentification
- Gestion du solde utilisateur
- Historique des paris

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Git

## Installation

1. **Cloner le repository**
   ```bash
   git clone https://github.com/lucrousseau21/MMIS6P2_django_betluc.git
   cd MMIS6P2_django_betluc
   ```

2. **Créer un environnement virtuel**
   ```bash
   # Sur Windows
   python -m venv venv
   venv\Scripts\activate

   # Sur Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d'environnement**
   - Créez un fichier `.env` à la racine du projet
   - Ajoutez les variables suivantes :
     ```
     DEBUG=True
     SECRET_KEY=votre_clé_secrète
     DATABASE_URL=sqlite:///db.sqlite3
     ```

5. **Effectuer les migrations de la base de données**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Créer un superutilisateur (admin)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Lancer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

8. **Accéder à l'application**
   - Site web : http://127.0.0.1:8000
   - Interface d'administration : http://127.0.0.1:8000/admin

## Structure du Projet

```
MMIS6P2_django_betluc/
├── superSite/              # Projet Django principal
│   ├── betluc/            # Application principale
│   │   ├── accounts/      # Gestion des utilisateurs
│   │   ├── teams/         # Gestion des équipes et matchs
│   │   └── bets/          # Gestion des paris
│   ├── static/            # Fichiers statiques (CSS, JS, images)
│   └── templates/         # Templates HTML
├── media/                 # Fichiers médias uploadés
├── requirements.txt       # Dépendances du projet
└── manage.py             # Script de gestion Django
```

## Utilisation

1. **Créer un compte**
   - Accédez à http://127.0.0.1:8000/accounts/register/
   - Remplissez le formulaire d'inscription

2. **Se connecter**
   - Accédez à http://127.0.0.1:8000/accounts/login/
   - Entrez vos identifiants

3. **Effectuer un pari**
   - Parcourez les matchs disponibles
   - Sélectionnez un match
   - Choisissez votre type de pari et le montant
   - Confirmez votre pari

## Développement

Pour contribuer au projet :

1. Créez une nouvelle branche
   ```bash
   git checkout -b feature/nouvelle-fonctionnalite
   ```

2. Faites vos modifications

3. Committez vos changements
   ```bash
   git add .
   git commit -m "Description des modifications"
   ```

4. Poussez vos modifications
   ```bash
   git push origin feature/nouvelle-fonctionnalite
   ```

## Support

Pour toute question ou problème, veuillez :
- Ouvrir une issue sur GitHub
- Contacter l'équipe de développement

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails. 