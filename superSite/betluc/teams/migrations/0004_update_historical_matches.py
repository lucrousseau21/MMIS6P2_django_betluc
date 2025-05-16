from django.db import migrations
import random
from datetime import datetime, timedelta

def update_historical_matches(apps, schema_editor):
    Match = apps.get_model('teams', 'Match')
    Matchday = apps.get_model('teams', 'Matchday')
    
    # Mettre à jour les journées jusqu'à la 20ème
    matchdays = Matchday.objects.filter(number__lte=20)
    for matchday in matchdays:
        matchday.is_completed = True
        matchday.save()
        
        # Mettre à jour tous les matchs de ces journées
        matches = Match.objects.filter(matchday=matchday)
        for match in matches:
            # Générer des scores aléatoires (entre 0 et 5)
            match.home_score = random.randint(0, 5)
            match.away_score = random.randint(0, 5)
            match.status = 'completed'
            # Mettre à jour le résultat en fonction des scores
            if match.home_score > match.away_score:
                match.result = 'home_win'
            elif match.home_score < match.away_score:
                match.result = 'away_win'
            else:
                match.result = 'draw'
            match.save()

def reverse_update_historical_matches(apps, schema_editor):
    Match = apps.get_model('teams', 'Match')
    Matchday = apps.get_model('teams', 'Matchday')
    
    # Remettre les journées en non terminées
    matchdays = Matchday.objects.filter(number__lte=20)
    for matchday in matchdays:
        matchday.is_completed = False
        matchday.save()
        
        # Remettre les matchs en statut à venir
        matches = Match.objects.filter(matchday=matchday)
        for match in matches:
            match.home_score = None
            match.away_score = None
            match.status = 'scheduled'
            match.result = 'pending'
            match.save()

class Migration(migrations.Migration):
    dependencies = [
        ('teams', '0003_update_match_statuses'),
    ]

    operations = [
        migrations.RunPython(update_historical_matches, reverse_update_historical_matches),
    ] 