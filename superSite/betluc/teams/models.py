from django.db import models
from django.utils import timezone
from accounts.models import Utilisateur
import random
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.management import call_command
from django.db import transaction

# Create your models here.

class League(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la ligue")
    country = models.CharField(max_length=100, verbose_name="Pays")
    logo = models.ImageField(upload_to='leagues_logos/', blank=True, null=True, verbose_name="Logo")
    
    class Meta:
        verbose_name = "Ligue"
        verbose_name_plural = "Ligues"
    
    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de l'équipe")
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='teams', verbose_name="Ligue")
    logo = models.ImageField(upload_to='teams_logos/', blank=True, null=True, verbose_name="Logo")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ville")
    founded_year = models.IntegerField(blank=True, null=True, verbose_name="Année de fondation")
    stadium = models.CharField(max_length=100, blank=True, verbose_name="Stade")
    
    class Meta:
        verbose_name = "Équipe"
        verbose_name_plural = "Équipes"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Matchday(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='matchdays', verbose_name="Ligue")
    number = models.PositiveIntegerField(verbose_name="Numéro de journée")
    date = models.DateField(verbose_name="Date")
    is_completed = models.BooleanField(default=False, verbose_name="Journée terminée")
    
    class Meta:
        verbose_name = "Journée"
        verbose_name_plural = "Journées"
        ordering = ['league', 'number']
        unique_together = ['league', 'number']
    
    def __str__(self):
        return f"{self.league.name} - Journée {self.number}"

class Match(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Programmé'),
        ('live', 'En cours'),
        ('completed', 'Terminé'),
    ]
    
    RESULT_CHOICES = [
        ('home_win', 'Victoire domicile'),
        ('draw', 'Match nul'),
        ('away_win', 'Victoire extérieur'),
        ('pending', 'En attente'),
    ]
    
    matchday = models.ForeignKey(Matchday, on_delete=models.CASCADE, related_name='matches')
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    date = models.DateTimeField()
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='pending')
    stadium = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"
    
    def save(self, *args, **kwargs):
        # Si le match est terminé et que les scores sont définis, mettre à jour le résultat
        if self.status == 'completed' and self.home_score is not None and self.away_score is not None:
            if self.home_score > self.away_score:
                self.result = 'home_win'
            elif self.away_score > self.home_score:
                self.result = 'away_win'
            else:
                self.result = 'draw'
        
        # Sauvegarder le match
        super().save(*args, **kwargs)
        
        # Si le match vient d'être marqué comme terminé, mettre à jour les paris
        if self.status == 'completed' and self.result in ['home_win', 'away_win', 'draw']:
            # Récupérer tous les paris en attente pour ce match
            pending_bets = Bet.objects.filter(
                match=self,
                status='pending'
            ).select_related('user')
            
            for bet in pending_bets:
                # Déterminer si le pari est gagné
                is_win = (
                    (bet.bet_type == 'home_win' and self.result == 'home_win') or
                    (bet.bet_type == 'draw' and self.result == 'draw') or
                    (bet.bet_type == 'away_win' and self.result == 'away_win')
                )
                
                with transaction.atomic():
                    # Mettre à jour le statut du pari
                    bet.status = 'won' if is_win else 'lost'
                    bet.save()
                    
                    # Si le pari est gagné, mettre à jour le solde de l'utilisateur
                    if is_win:
                        user = bet.user
                        winnings = bet.amount * bet.odds
                        user.balance += winnings
                        user.save()

class Odds(models.Model):
    match = models.OneToOneField(Match, on_delete=models.CASCADE, related_name='odds', verbose_name="Match")
    home_win = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Cote victoire domicile")
    draw = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Cote match nul")
    away_win = models.DecimalField(max_digits=4, decimal_places=2, verbose_name="Cote victoire extérieur")
    
    class Meta:
        verbose_name = "Cote"
        verbose_name_plural = "Cotes"
    
    def __str__(self):
        return f"Cotes pour {self.match}"
    
    def get_odds_for_bet_type(self, bet_type):
        """Retourne la cote correspondant au type de pari"""
        if bet_type == 'home_win':
            return self.home_win
        elif bet_type == 'draw':
            return self.draw
        elif bet_type == 'away_win':
            return self.away_win
        return None
    
    @classmethod
    def generate_random_odds(cls):
        """Génère des cotes aléatoires entre 1 et 5"""
        return (
            round(random.uniform(1, 5), 2),
            round(random.uniform(1, 5), 2),
            round(random.uniform(1, 5), 2)
        )
    
    @classmethod
    def create_for_match(cls, match):
        """Crée des cotes pour un match spécifique"""
        home_win, draw, away_win = cls.generate_random_odds()
        return cls.objects.create(
            match=match,
            home_win=home_win,
            draw=draw,
            away_win=away_win
        )

class Bet(models.Model):
    BET_TYPES = [
        ('home_win', 'Victoire domicile'),
        ('draw', 'Match nul'),
        ('away_win', 'Victoire extérieur'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('won', 'Gagné'),
        ('lost', 'Perdu'),
    ]
    
    user = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='bets')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='bets')
    bet_type = models.CharField(max_length=20, choices=BET_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    odds = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.match} - {self.get_bet_type_display()}"
    
    @property
    def potential_win(self):
        return self.amount * self.odds
    
    def check_result(self):
        """Vérifie le résultat du pari après la fin du match"""
        if self.match.status != 'completed':
            return
        
        if self.bet_type == 'home_win' and self.match.home_score > self.match.away_score:
            self.status = 'won'
        elif self.bet_type == 'away_win' and self.match.away_score > self.match.home_score:
            self.status = 'won'
        elif self.bet_type == 'draw' and self.match.home_score == self.match.away_score:
            self.status = 'won'
        else:
            self.status = 'lost'
        
        self.save()
