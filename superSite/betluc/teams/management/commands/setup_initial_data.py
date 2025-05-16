from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction
from teams.models import Match, Matchday, Team, League
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Initialise la base de données avec les équipes, matchs et utilisateurs'

    def handle(self, *args, **kwargs):
        print("Initialisation de la base de données...")
        
        # Charger les fixtures
        print("Chargement des données initiales...")
        call_command('loaddata', 'teams/fixtures/initial_data.json')
        
        # Générer les matchs pour les journées restantes (4 à 30)
        print("Génération des matchs...")
        teams = list(Team.objects.all())
        league = League.objects.get(name="Ligue 1")
        current_date = datetime.now()
        
        with transaction.atomic():
            for day in range(4, 31):  # Commencer à la journée 4
                matchday = Matchday.objects.create(
                    league=league,
                    number=day,
                    date=current_date.date(),
                    is_completed=False
                )
                
                # Générer 5 matchs par journée
                for _ in range(5):
                    home_team = random.choice(teams)
                    away_team = random.choice([t for t in teams if t != home_team])
                    
                    match = Match.objects.create(
                        matchday=matchday,
                        home_team=home_team,
                        away_team=away_team,
                        date=current_date + timedelta(hours=random.randint(0, 48)),
                        stadium=f"Stade de {home_team.name}",
                        status='scheduled'
                    )
                
                current_date += timedelta(days=7)
        
        # Générer les utilisateurs aléatoires
        print("Génération des utilisateurs et des paris...")
        call_command('generate_random_users')
        
        print("Configuration terminée avec succès !") 