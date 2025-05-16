from django.core.management.base import BaseCommand
from teams.models import Match

class Command(BaseCommand):
    help = 'Supprime le match en double Marseille vs PSG'

    def handle(self, *args, **options):
        try:
            # Trouver le match à supprimer (ID 43)
            match = Match.objects.get(id=43)
            
            # Vérifier que c'est bien le bon match
            if (match.home_team.name == 'Olympique de Marseille' and 
                match.away_team.name == 'Paris Saint-Germain'):
                
                # Supprimer le match
                match.delete()
                self.stdout.write(self.style.SUCCESS(
                    f"Match {match.id} (Marseille vs PSG du {match.date}) a été supprimé avec succès"
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    "Le match trouvé ne correspond pas à Marseille vs PSG"
                ))
                
        except Match.DoesNotExist:
            self.stdout.write(self.style.ERROR("Match ID 43 non trouvé"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors de la suppression : {str(e)}")) 