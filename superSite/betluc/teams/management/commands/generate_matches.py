from django.core.management.base import BaseCommand
from teams.models import League, Team, Matchday, Match, Odds
from django.utils import timezone
from datetime import timedelta
import random
import itertools

class Command(BaseCommand):
    help = 'Génère les journées et les matchs pour une ligue spécifique'

    def add_arguments(self, parser):
        parser.add_argument('league_id', type=int, help='ID de la ligue pour laquelle générer les matchs')
        parser.add_argument('--start-date', type=str, help='Date de début au format YYYY-MM-DD', default=None)
        parser.add_argument('--clear', action='store_true', help='Effacer les journées et matchs existants')

    def handle(self, *args, **options):
        league_id = options['league_id']
        start_date_str = options['start_date']
        clear = options['clear']
        
        try:
            league = League.objects.get(id=league_id)
        except League.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'La ligue avec l\'ID {league_id} n\'existe pas'))
            return
        
        teams = Team.objects.filter(league=league)
        if teams.count() < 2:
            self.stdout.write(self.style.ERROR(f'Il faut au moins 2 équipes dans la ligue pour générer des matchs'))
            return
        
        if clear:
            # Supprimer les journées et matchs existants pour cette ligue
            matchdays = Matchday.objects.filter(league=league)
            matches_count = Match.objects.filter(matchday__in=matchdays).count()
            matchdays.delete()
            self.stdout.write(self.style.WARNING(f'Suppression de {matches_count} matchs et de toutes les journées pour {league.name}'))
        
        # Définir la date de début
        if start_date_str:
            try:
                start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(self.style.ERROR('Format de date invalide. Utilisez YYYY-MM-DD'))
                return
        else:
            start_date = timezone.now().date()
        
        # Générer le calendrier des matchs
        self.generate_schedule(league, teams, start_date)
        
        self.stdout.write(self.style.SUCCESS(f'Génération du calendrier terminée pour {league.name}'))
    
    def generate_schedule(self, league, teams, start_date):
        teams_list = list(teams)
        num_teams = len(teams_list)
        
        if num_teams % 2 != 0:
            # Si le nombre d'équipes est impair, ajouter une équipe fictive pour les journées de repos
            teams_list.append(None)
            num_teams += 1
        
        # Nombre de journées par phase (aller et retour)
        num_rounds = num_teams - 1
        matches_per_round = num_teams // 2
        
        # Créer une liste circulaire des équipes
        teams_circle = teams_list.copy()
        
        # Générer les combinaisons de matchs pour la phase aller
        first_half_schedule = []
        for round_num in range(num_rounds):
            round_matches = []
            
            # Pour chaque journée, faire jouer les équipes opposées dans le cercle
            for i in range(matches_per_round):
                home_idx = i
                away_idx = num_teams - 1 - i
                
                # Si c'est la première équipe, elle joue contre la dernière
                if i == 0:
                    home_team = teams_circle[0]
                    away_team = teams_circle[-1]
                else:
                    home_team = teams_circle[home_idx]
                    away_team = teams_circle[away_idx]
                
                if home_team is not None and away_team is not None:
                    # Alterner domicile/extérieur pour chaque équipe
                    if round_num % 2 == 1 and i > 0:
                        home_team, away_team = away_team, home_team
                    round_matches.append((home_team, away_team))
            
            first_half_schedule.append(round_matches)
            
            # Faire tourner le cercle (sauf la première équipe)
            teams_circle = [teams_circle[0]] + [teams_circle[-1]] + teams_circle[1:-1]
        
        # Phase retour : inverser domicile/extérieur
        second_half_schedule = [
            [(away, home) for home, away in round_matches]
            for round_matches in first_half_schedule
        ]
        
        # Fusionner les deux phases
        full_schedule = first_half_schedule + second_half_schedule
        
        # Créer les journées et les matchs
        current_date = start_date
        for round_num, round_matches in enumerate(full_schedule, 1):
            # Créer la journée
            matchday = Matchday.objects.create(
                league=league,
                number=round_num,
                date=current_date,
                is_completed=False
            )
            self.stdout.write(f'Journée {round_num} créée pour le {current_date}')
            
            # Créer les matchs de cette journée
            for home_team, away_team in round_matches:
                # Générer une heure aléatoire entre 14h et 21h
                hour = random.randint(14, 21)
                minute = random.choice([0, 15, 30, 45])
                match_datetime = timezone.datetime.combine(
                    current_date,
                    timezone.datetime.min.time().replace(hour=hour, minute=minute)
                )
                match_datetime = timezone.make_aware(match_datetime)
                
                match = Match.objects.create(
                    matchday=matchday,
                    home_team=home_team,
                    away_team=away_team,
                    date=match_datetime,
                    status='scheduled'
                )
                self.stdout.write(f'  Match créé: {match}')
                
                # Générer des cotes pour ce match
                Odds.create_for_match(match)
            
            # Passer à la semaine suivante pour la prochaine journée
            current_date += timedelta(days=7) 