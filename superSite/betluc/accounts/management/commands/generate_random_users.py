from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db import transaction
from accounts.models import Utilisateur
from teams.models import Match, Bet
from decimal import Decimal
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Génère 30 utilisateurs aléatoires avec des paris aléatoires'

    def handle(self, *args, **kwargs):
        # Liste de prénoms et noms pour générer des noms d'utilisateur
        prenoms = ['Jean', 'Marie', 'Pierre', 'Sophie', 'Lucas', 'Emma', 'Thomas', 'Julie', 'Nicolas', 'Laura',
                   'Antoine', 'Camille', 'Maxime', 'Léa', 'Alexandre', 'Chloé', 'Quentin', 'Manon', 'Romain', 'Sarah']
        noms = ['Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Richard', 'Petit', 'Durand', 'Leroy', 'Moreau',
                'Simon', 'Laurent', 'Michel', 'Lefebvre', 'Garcia', 'David', 'Bertrand', 'Roux', 'Vincent', 'Fournier']

        # Types de paris possibles
        bet_types = ['home_win', 'draw', 'away_win']

        # Récupérer tous les matchs
        matches = Match.objects.all()
        if not matches:
            self.stdout.write(self.style.ERROR('Aucun match trouvé dans la base de données'))
            return

        with transaction.atomic():
            # Créer 30 utilisateurs
            for i in range(30):
                # Générer un nom d'utilisateur unique
                username = f"{random.choice(prenoms)}{random.choice(noms)}{random.randint(1, 999)}"
                while Utilisateur.objects.filter(username=username).exists():
                    username = f"{random.choice(prenoms)}{random.choice(noms)}{random.randint(1, 999)}"

                # Créer l'utilisateur avec un solde initial aléatoire entre 100 et 1000€
                user = Utilisateur.objects.create(
                    username=username,
                    email=f"{username.lower()}@gmail.com",
                    password=make_password('azerty'),
                    balance=Decimal(str(random.randint(100, 1000)))
                )

                # Générer entre 5 et 15 paris aléatoires pour chaque utilisateur
                num_bets = random.randint(5, 15)
                for _ in range(num_bets):
                    match = random.choice(matches)
                    bet_type = random.choice(bet_types)
                    amount = Decimal(str(random.randint(10, 100)))
                    odds = Decimal(str(round(random.uniform(1.1, 3.0), 2)))
                    
                    # Déterminer le statut du pari en fonction du résultat du match
                    if match.status == 'completed':
                        if match.result == bet_type:
                            status = 'won'
                        else:
                            status = 'lost'
                    else:
                        status = 'pending'

                    # Créer le pari
                    bet = Bet.objects.create(
                        user=user,
                        match=match,
                        bet_type=bet_type,
                        amount=amount,
                        odds=odds,
                        status=status
                    )

                    # Mettre à jour le solde de l'utilisateur en fonction du résultat
                    if status == 'won':
                        user.balance += bet.potential_win
                    elif status == 'lost':
                        user.balance -= amount
                    user.save()

                self.stdout.write(self.style.SUCCESS(f'Utilisateur créé : {username} ({username.lower()}@gmail.com) avec {num_bets} paris'))

        self.stdout.write(self.style.SUCCESS('Génération des utilisateurs et des paris terminée avec succès')) 