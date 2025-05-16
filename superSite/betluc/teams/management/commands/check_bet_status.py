from django.core.management.base import BaseCommand
from teams.models import Bet, Match
from django.db.models import Q

class Command(BaseCommand):
    help = 'Vérifie l\'état des paris et des matchs'

    def handle(self, *args, **options):
        # Vérifier tous les paris en attente
        pending_bets = Bet.objects.filter(status='pending').select_related('match', 'user')
        
        self.stdout.write(f"Nombre total de paris en attente : {pending_bets.count()}")
        
        for bet in pending_bets:
            self.stdout.write("\n" + "="*50)
            self.stdout.write(f"Pari ID: {bet.id}")
            self.stdout.write(f"Utilisateur: {bet.user.username}")
            self.stdout.write(f"Match: {bet.match}")
            self.stdout.write(f"Type de pari: {bet.get_bet_type_display()}")
            self.stdout.write(f"Montant: {bet.amount}€")
            self.stdout.write(f"Cote: {bet.odds}")
            self.stdout.write(f"Statut du match: {bet.match.get_status_display()}")
            self.stdout.write(f"Score: {bet.match.home_score} - {bet.match.away_score}")
            self.stdout.write(f"Résultat du match: {bet.match.get_result_display()}")
            
            # Vérifier si le match devrait être terminé
            if bet.match.status != 'completed':
                self.stdout.write(self.style.WARNING(
                    f"Le match n'est pas marqué comme terminé alors qu'il devrait l'être"
                ))
            
            # Vérifier si le résultat correspond au pari
            is_win = (
                (bet.bet_type == 'home_win' and bet.match.result == 'home_win') or
                (bet.bet_type == 'draw' and bet.match.result == 'draw') or
                (bet.bet_type == 'away_win' and bet.match.result == 'away_win')
            )
            
            if bet.match.status == 'completed':
                self.stdout.write(
                    f"Le pari devrait être {'gagné' if is_win else 'perdu'}"
                ) 