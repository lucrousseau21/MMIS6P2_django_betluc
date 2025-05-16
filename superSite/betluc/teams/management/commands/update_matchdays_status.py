from django.core.management.base import BaseCommand
from teams.models import Matchday, Match
from django.db import transaction
from django.db.models import Count, Q

class Command(BaseCommand):
    help = 'Met à jour le statut des journées en fonction de leurs matchs'

    def handle(self, *args, **options):
        try:
            # Récupérer toutes les journées
            matchdays = Matchday.objects.all()
            
            with transaction.atomic():
                for matchday in matchdays:
                    # Compter le nombre total de matchs et le nombre de matchs terminés
                    match_stats = Match.objects.filter(matchday=matchday).aggregate(
                        total_matches=Count('id'),
                        completed_matches=Count('id', filter=Q(status='completed'))
                    )
                    
                    # Si tous les matchs sont terminés, marquer la journée comme terminée
                    if (match_stats['total_matches'] > 0 and 
                        match_stats['total_matches'] == match_stats['completed_matches']):
                        matchday.is_completed = True
                        matchday.save()
                        self.stdout.write(
                            f"Journée {matchday.number} ({matchday.league.name}) marquée comme terminée - "
                            f"{match_stats['completed_matches']}/{match_stats['total_matches']} matchs terminés"
                        )
                    else:
                        self.stdout.write(
                            f"Journée {matchday.number} ({matchday.league.name}) non terminée - "
                            f"{match_stats['completed_matches']}/{match_stats['total_matches']} matchs terminés"
                        )
            
            self.stdout.write(self.style.SUCCESS(
                "\nMise à jour des statuts des journées terminée avec succès !"
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors de la mise à jour : {str(e)}")) 