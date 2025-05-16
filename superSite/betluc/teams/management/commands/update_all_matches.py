from django.core.management.base import BaseCommand
from teams.models import Match, Matchday
import random
from django.db import transaction

class Command(BaseCommand):
    help = 'Met à jour tous les matchs jusqu\'à la journée 30 avec des résultats aléatoires'

    def add_arguments(self, parser):
        parser.add_argument('--until', type=int, default=30, help='Journée jusqu\'à laquelle mettre à jour les matchs (défaut: 30)')

    def handle(self, *args, **options):
        until_matchday = options['until']
        
        try:
            # Récupérer toutes les journées jusqu'à la journée spécifiée
            matchdays = Matchday.objects.filter(number__lte=until_matchday).order_by('number')
            
            if not matchdays.exists():
                self.stdout.write(self.style.ERROR(f"Aucune journée trouvée jusqu'à la journée {until_matchday}"))
                return
            
            total_matches_updated = 0
            
            for matchday in matchdays:
                matches = Match.objects.filter(matchday=matchday)
                self.stdout.write(f"\nTraitement de la journée {matchday.number} ({matches.count()} matchs)")
                
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
                        total_matches_updated += 1
                        
                        self.stdout.write(
                            f"  {match.home_team} {home_score} - {away_score} {match.away_team} "
                            f"(Résultat : {match.get_result_display()})"
                        )
                
                # Marquer la journée comme terminée
                matchday.is_completed = True
                matchday.save()
            
            self.stdout.write(self.style.SUCCESS(
                f"\nMise à jour terminée ! {total_matches_updated} matchs ont été mis à jour jusqu'à la journée {until_matchday}"
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors de la mise à jour : {str(e)}")) 