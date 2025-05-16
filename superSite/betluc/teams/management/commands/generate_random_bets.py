from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from accounts.models import Utilisateur
from teams.models import Match, Bet, Matchday
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Génère des paris aléatoires pour les utilisateurs sur les matchs terminés'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-bets-per-user',
            type=int,
            default=5,
            help='Nombre maximum de paris par utilisateur'
        )
        parser.add_argument(
            '--min-amount',
            type=float,
            default=5.0,
            help='Montant minimum des paris'
        )
        parser.add_argument(
            '--max-amount',
            type=float,
            default=50.0,
            help='Montant maximum des paris'
        )

    def handle(self, *args, **options):
        # Récupérer tous les utilisateurs
        users = Utilisateur.objects.all()
        if not users.exists():
            self.stdout.write(self.style.ERROR('Aucun utilisateur trouvé'))
            return

        # Récupérer les journées terminées
        completed_matchdays = Matchday.objects.filter(is_completed=True)
        if not completed_matchdays.exists():
            self.stdout.write(self.style.ERROR('Aucune journée terminée trouvée'))
            return

        # Récupérer les matchs terminés de ces journées
        completed_matches = Match.objects.filter(
            matchday__in=completed_matchdays,
            status='completed'
        )
        if not completed_matches.exists():
            self.stdout.write(self.style.ERROR('Aucun match terminé trouvé'))
            return

        # Types de paris possibles
        bet_types = ['home_win', 'away_win', 'draw']
        
        # Compteurs pour les statistiques
        total_bets = 0
        total_won = 0
        total_lost = 0

        # Pour chaque utilisateur
        for user in users:
            # Nombre aléatoire de paris pour cet utilisateur
            num_bets = random.randint(1, options['max_bets_per_user'])
            
            # Sélectionner aléatoirement des matchs pour cet utilisateur
            user_matches = random.sample(list(completed_matches), min(num_bets, completed_matches.count()))
            
            for match in user_matches:
                # Vérifier si l'utilisateur n'a pas déjà parié sur ce match
                if Bet.objects.filter(user=user, match=match).exists():
                    continue

                # Générer un pari aléatoire
                bet_type = random.choice(bet_types)
                amount = Decimal(str(round(random.uniform(options['min_amount'], options['max_amount']), 2)))
                
                # Récupérer la cote correspondante
                odds = match.odds
                if bet_type == 'home_win':
                    odds_value = odds.home_win
                elif bet_type == 'away_win':
                    odds_value = odds.away_win
                else:  # draw
                    odds_value = odds.draw

                # Déterminer si le pari est gagné ou perdu
                if bet_type == match.result:
                    status = 'won'
                    total_won += 1
                else:
                    status = 'lost'
                    total_lost += 1

                # Créer le pari
                bet = Bet.objects.create(
                    user=user,
                    match=match,
                    bet_type=bet_type,
                    amount=amount,
                    odds=odds_value,
                    status=status,
                    created_at=match.date - timezone.timedelta(days=random.randint(1, 3))  # Pari placé quelques jours avant le match
                )
                
                total_bets += 1

                # Mettre à jour la balance de l'utilisateur
                if status == 'won':
                    user.add_balance(bet.potential_win)
                else:
                    user.remove_balance(bet.amount)

        self.stdout.write(self.style.SUCCESS(
            f'Génération terminée :\n'
            f'- {total_bets} paris créés\n'
            f'- {total_won} paris gagnés\n'
            f'- {total_lost} paris perdus'
        )) 