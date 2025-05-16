from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from teams.models import League, Team, Matchday, Match, Bet, Odds
from accounts.models import Utilisateur
import random
from datetime import datetime, timedelta
import itertools
import pytz

class Command(BaseCommand):
    help = 'Initialise les données de la ligue avec les équipes, matchs et paris'

    def handle(self, *args, **options):
        self.stdout.write('Début de l\'initialisation des données...')

        # 1. Créer la ligue
        league, _ = League.objects.get_or_create(
            name="Ligue 1",
            country="France"
        )

        # 2. Créer les équipes
        teams_data = [
            ("Paris Saint-Germain", "Paris", "Parc des Princes"),
            ("Olympique de Marseille", "Marseille", "Orange Vélodrome"),
            ("AS Monaco", "Monaco", "Stade Louis II"),
            ("OGC Nice", "Nice", "Allianz Riviera"),
            ("LOSC Lille", "Lille", "Stade Pierre-Mauroy"),
            ("RC Strasbourg", "Strasbourg", "Stade de la Meinau"),
            ("Olympique Lyonnais", "Lyon", "Groupama Stadium"),
            ("Stade Brestois", "Brest", "Stade Francis-Le Blé"),
            ("RC Lens", "Lens", "Stade Bollaert-Delelis"),
            ("AJ Auxerre", "Auxerre", "Stade de l'Abbé-Deschamps"),
            ("Stade Rennais", "Rennes", "Roazhon Park"),
            ("Toulouse FC", "Toulouse", "Stadium de Toulouse"),
            ("Angers SCO", "Angers", "Stade Raymond-Kopa"),
            ("Stade de Reims", "Reims", "Stade Auguste-Delaune"),
            ("FC Nantes", "Nantes", "Stade de la Beaujoire"),
            ("Le Havre AC", "Le Havre", "Stade Océane"),
            ("AS Saint-Étienne", "Saint-Étienne", "Stade Geoffroy-Guichard"),
            ("Montpellier HSC", "Montpellier", "Stade de la Mosson"),
        ]

        # Supprimer les anciennes équipes
        Team.objects.all().delete()
        
        # Créer les nouvelles équipes
        teams = []
        for name, city, stadium in teams_data:
            team = Team.objects.create(
                name=name,
                league=league,
                city=city,
                stadium=stadium
            )
            teams.append(team)

        # 3. Créer les journées et matchs
        Matchday.objects.all().delete()
        Match.objects.all().delete()
        Bet.objects.all().delete()
        Odds.objects.all().delete()

        # Date de début de la saison
        start_date = datetime(2024, 8, 18, 20, 0, tzinfo=pytz.UTC)
        
        # Générer toutes les combinaisons de matchs possibles
        all_matches = list(itertools.permutations(teams, 2))
        
        # Répartir les matchs sur 36 journées
        matches_per_day = len(all_matches) // 36
        remaining_matches = len(all_matches) % 36
        
        current_match_index = 0
        for day in range(1, 37):
            # Calculer la date de la journée
            matchday_date = start_date + timedelta(days=(day-1)*7)
            
            # Créer la journée
            matchday = Matchday.objects.create(
                league=league,
                number=day,
                date=matchday_date.date(),
                is_completed=day <= 30  # Les 30 premières journées sont terminées
            )
            
            # Nombre de matchs pour cette journée
            num_matches = matches_per_day + (1 if day <= remaining_matches else 0)
            
            # Créer les matchs pour cette journée
            for i in range(num_matches):
                if current_match_index < len(all_matches):
                    home_team, away_team = all_matches[current_match_index]
                    match_time = matchday_date + timedelta(hours=i*2)  # Espacer les matchs de 2h
                    
                    # Générer des scores aléatoires pour les 30 premières journées
                    if day <= 30:
                        home_score = random.randint(0, 4)
                        away_score = random.randint(0, 4)
                        status = "completed"
                    else:
                        home_score = None
                        away_score = None
                        status = "scheduled"
                    
                    match = Match.objects.create(
                        matchday=matchday,
                        home_team=home_team,
                        away_team=away_team,
                        date=match_time,
                        home_score=home_score,
                        away_score=away_score,
                        status=status
                    )
                    
                    # Créer les cotes pour le match
                    Odds.create_for_match(match)
                    
                    current_match_index += 1

        # 4. Créer les parieurs et leurs paris
        # Supprimer les anciens parieurs
        Utilisateur.objects.filter(username__startswith='parieur_').delete()
        
        # Créer 30 nouveaux parieurs
        for i in range(1, 31):
            username = f'parieur_{i}'
            user = Utilisateur.objects.create_user(
                username=username,
                email=f'{username}@example.com',
                password='password123',
                balance=1000.0  # Solde initial de 1000€
            )
            
            # Faire des paris aléatoires sur les matchs non joués
            for match in Match.objects.filter(status="scheduled"):
                if random.random() < 0.3:  # 30% de chance de parier sur un match
                    # Choisir un type de pari aléatoire
                    bet_type = random.choice(['home_win', 'draw', 'away_win'])
                    amount = random.randint(10, 100)  # Pari entre 10€ et 100€
                    
                    # Récupérer les cotes
                    odds = match.odds.get_odds_for_bet_type(bet_type)
                    
                    # Créer le pari
                    Bet.objects.create(
                        user=user,
                        match=match,
                        bet_type=bet_type,
                        amount=amount,
                        odds=odds,
                        status='pending'
                    )

        self.stdout.write(self.style.SUCCESS('Initialisation des données terminée avec succès !')) 