from django.core.management.base import BaseCommand
from teams.models import Match, Matchday
import random
from django.db import transaction

class Command(BaseCommand):
    help = 'Met à jour tous les matchs de la 30ème journée avec des résultats aléatoires'

    def handle(self, *args, **options):
        try:
            # Trouver la 30ème journée
            matchday = Matchday.objects.get(number=30)
            matches = Match.objects.filter(matchday=matchday)
            
            self.stdout.write(f"Nombre de matchs trouvés pour la journée 30 : {matches.count()}")
            
            with transaction.atomic():
                for match in matches:
                    # Générer des scores aléatoires (0 à 4 buts par équipe)
                    home_score = random.randint(0, 4)
                    away_score = random.randint(0, 4)
                    
                    # Mettre à jour le match
                    match.status = 'completed'
                    match.home_score = home_score
                    match.away_score = away_score
                    
                    # Définir le résultat
                    if home_score > away_score:
                        match.result = 'home_win'
                    elif away_score > home_score:
                        match.result = 'away_win'
                    else:
                        match.result = 'draw'
                    
                    match.save()
                    
                    self.stdout.write(
                        f"Match mis à jour : {match.home_team} {home_score} - {away_score} {match.away_team} "
                        f"(Résultat : {match.get_result_display()})"
                    )
            
            self.stdout.write(self.style.SUCCESS(
                f"\nTous les matchs de la journée 30 ont été mis à jour avec succès !"
            ))
            
        except Matchday.DoesNotExist:
            self.stdout.write(self.style.ERROR("Journée 30 non trouvée"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors de la mise à jour : {str(e)}")) 