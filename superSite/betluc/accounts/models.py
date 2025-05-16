from django.db import models
from django.contrib.auth.models import AbstractUser

class Utilisateur(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=20.00, verbose_name="Solde")
    
    def __str__(self):
        return self.username

    def add_balance(self, amount):
        """Ajoute un montant au solde de l'utilisateur"""
        self.balance += amount
        self.save(update_fields=['balance'])
    
    def remove_balance(self, amount):
        """Retire un montant du solde de l'utilisateur"""
        if self.balance >= amount:
            self.balance -= amount
            self.save(update_fields=['balance'])
            return True
        return False
