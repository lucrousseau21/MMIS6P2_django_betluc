from django.db import migrations, models
import django.db.models.deletion

def convert_league_data(apps, schema_editor):
    League = apps.get_model('teams', 'League')
    Team = apps.get_model('teams', 'Team')
    
    # Vérifier la structure de la table
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(teams_team)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'league' not in columns:
            print("La colonne 'league' n'existe pas dans la table teams_team")
            return
            
        # Récupérer les valeurs uniques de league
        cursor.execute("SELECT DISTINCT league FROM teams_team WHERE league IS NOT NULL")
        league_names = [row[0] for row in cursor.fetchall()]
    
    # Créer les ligues
    leagues = {}
    for league_name in league_names:
        if league_name and league_name != 'league_id':  # Ignorer les valeurs invalides
            league, created = League.objects.get_or_create(
                name=league_name,
                defaults={'country': 'France'}
            )
            leagues[league_name] = league
    
    # Convertir le champ pour chaque équipe
    with schema_editor.connection.cursor() as cursor:
        for league_name, league in leagues.items():
            cursor.execute(
                "UPDATE teams_team SET league_new_id = %s WHERE league = %s",
                [league.id, league_name]
            )

def reverse_migration(apps, schema_editor):
    Team = apps.get_model('teams', 'Team')
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            UPDATE teams_team 
            SET league = (
                SELECT name 
                FROM teams_league 
                WHERE teams_league.id = teams_team.league_new_id
            )
        """)

class Migration(migrations.Migration):
    dependencies = [
        ('teams', '0007_add_league_new_field'),
    ]

    operations = [
        # 1. Exécuter la fonction de conversion
        migrations.RunPython(convert_league_data, reverse_migration),
        
        # 2. Supprimer l'ancien champ
        migrations.RemoveField(
            model_name='team',
            name='league',
        ),
        
        # 3. Renommer le nouveau champ
        migrations.RenameField(
            model_name='team',
            old_name='league_new',
            new_name='league',
        ),
        
        # 4. Rendre le champ obligatoire
        migrations.AlterField(
            model_name='team',
            name='league',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='teams',
                to='teams.league',
                verbose_name='Ligue'
            ),
        ),
    ] 