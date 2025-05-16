from django.core.management.base import BaseCommand
from django.db import transaction
from teams.models import Bet, Match

class Command(BaseCommand):
    help = 'Met à jour le statut des paris pour les matchs terminés'

    def handle(self, *args, **options):
        # Récupérer tous les paris en attente pour les matchs terminés
        pending_bets = Bet.objects.filter(
            match__status='completed',
            status='pending'
        ).select_related('match', 'user')

        updated_count = 0
        with transaction.atomic():
            for bet in pending_bets:
                # Vérifier si le pari est gagnant
                is_win = (
                    (bet.bet_type == 'home_win' and bet.match.result == 'home_win') or
                    (bet.bet_type == 'draw' and bet.match.result == 'draw') or
                    (bet.bet_type == 'away_win' and bet.match.result == 'away_win')
                )

                # Mettre à jour le statut du pari
                bet.status = 'won' if is_win else 'lost'
                bet.save(update_fields=['status'])

                # Si le pari est gagnant, ajouter les gains au solde de l'utilisateur
                if is_win:
                    # Calculer les gains (mise * cote)
                    gains = bet.amount * bet.odds
                    bet.user.add_balance(gains)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Pari {bet.id} gagné pour {bet.user.username}. '
                            f'Gains: {gains}€ ajoutés au solde.'
                        )
                    )

                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Statut mis à jour pour {updated_count} paris'
            )
        ) 