from django.db import migrations

def update_match_statuses(apps, schema_editor):
    Match = apps.get_model('teams', 'Match')
    # Pour tous les matchs qui ont un score mais qui sont marqués comme terminés
    matches = Match.objects.filter(
        home_score__isnull=False,
        away_score__isnull=False,
        status='completed'
    )
    # On les met en statut 'live' s'ils ont un score mais ne sont pas vraiment terminés
    for match in matches:
        match.status = 'live'
        match.save()

def reverse_update_match_statuses(apps, schema_editor):
    Match = apps.get_model('teams', 'Match')
    # Pour tous les matchs en cours qui ont un score
    matches = Match.objects.filter(
        home_score__isnull=False,
        away_score__isnull=False,
        status='live'
    )
    # On les remet en statut 'completed'
    for match in matches:
        match.status = 'completed'
        match.save()

class Migration(migrations.Migration):
    dependencies = [
        ('teams', '0002_match_bet_matchday_match_matchday_odds'),
    ]

    operations = [
        migrations.RunPython(update_match_statuses, reverse_update_match_statuses),
    ] 