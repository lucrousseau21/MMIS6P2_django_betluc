from django.core.management.base import BaseCommand
from teams.models import Match, Bet

class Command(BaseCommand):
    help = 'Affiche des informations détaillées sur les matchs Marseille vs PSG'

    def handle(self, *args, **options):
        # Trouver tous les matchs Marseille vs PSG
        matches = Match.objects.filter(
            home_team__name='Olympique de Marseille',
            away_team__name='Paris Saint-Germain'
        ).order_by('date')
        
        self.stdout.write(f"\nNombre de matchs trouvés : {matches.count()}")
        
        for match in matches:
            self.stdout.write("\n" + "="*50)
            self.stdout.write("\n=== INFORMATIONS DU MATCH ===")
            self.stdout.write(f"ID: {match.id}")
            self.stdout.write(f"Date: {match.date}")
            self.stdout.write(f"Statut: {match.get_status_display()} ({match.status})")
            self.stdout.write(f"Score: {match.home_score} - {match.away_score}")
            self.stdout.write(f"Résultat: {match.get_result_display()} ({match.result})")
            
            # Vérifier les paris
            bets = Bet.objects.filter(match=match).select_related('user')
            self.stdout.write("\n=== PARIS ASSOCIÉS ===")
            self.stdout.write(f"Nombre total de paris: {bets.count()}")
            
            for bet in bets:
                self.stdout.write("\n" + "-"*30)
                self.stdout.write(f"Pari ID: {bet.id}")
                self.stdout.write(f"Utilisateur: {bet.user.username}")
                self.stdout.write(f"Type de pari: {bet.get_bet_type_display()} ({bet.bet_type})")
                self.stdout.write(f"Montant: {bet.amount}€")
                self.stdout.write(f"Cote: {bet.odds}")
                self.stdout.write(f"Statut: {bet.get_status_display()} ({bet.status})")
                
                # Vérifier si le pari devrait être gagné
                is_win = (
                    (bet.bet_type == 'home_win' and match.result == 'home_win') or
                    (bet.bet_type == 'draw' and match.result == 'draw') or
                    (bet.bet_type == 'away_win' and match.result == 'away_win')
                )
                self.stdout.write(f"Devrait être: {'gagné' if is_win else 'perdu'}")
            
            self.stdout.write("\n" + "="*50) 