from django.core.management.base import BaseCommand
from django.db import transaction
from teams.models import Match

class Command(BaseCommand):
    help = 'Met à jour les résultats des matchs terminés'

    def handle(self, *args, **options):
        # Récupérer tous les matchs terminés
        completed_matches = Match.objects.filter(status='completed')
        updated_count = 0

        with transaction.atomic():
            for match in completed_matches:
                # Mettre à jour le résultat sans sauvegarder
                match.update_result()
                # Sauvegarder explicitement
                match.save(update_fields=['result'])
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} match results')
        ) 