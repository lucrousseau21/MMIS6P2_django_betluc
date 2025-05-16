from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UtilisateurCreationForm
from django.db import transaction
from django.db.models import Sum, Count, Case, When, Value, IntegerField, F, ExpressionWrapper, DecimalField
from .models import Utilisateur
from decimal import Decimal

def register_view(request):
    if request.method == 'POST':
        form = UtilisateurCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Compte créé avec succès pour {user.username}!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Erreur lors de la création du compte. Veuillez réessayer.')
    else:
        form = UtilisateurCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue, {username}!')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe invalide.')
        else:
            messages.error(request, 'Formulaire invalide. Veuillez réessayer.')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès!')
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

@login_required
@transaction.atomic
def deposit(request):
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', 0))
            
            # Vérifier que le montant est valide
            if amount < Decimal('10') or amount > Decimal('1000'):
                messages.error(request, "Le montant doit être compris entre 10€ et 1000€")
                return redirect('accounts:profile')
            
            # Mettre à jour le solde de l'utilisateur
            user = request.user
            user.balance += amount
            user.save()
            
            messages.success(request, f"Votre dépôt de {amount}€ a été effectué avec succès !")
            return redirect('accounts:profile')
            
        except (ValueError, TypeError):
            messages.error(request, "Montant invalide")
            return redirect('accounts:profile')
    
    return redirect('accounts:profile')

@login_required
@transaction.atomic
def withdraw(request):
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', 0))
            
            # Vérifier que le montant est valide
            if amount < Decimal('10') or amount > Decimal('1000'):
                messages.error(request, "Le montant doit être compris entre 10€ et 1000€")
                return redirect('accounts:profile')
            
            # Vérifier que l'utilisateur a assez d'argent
            user = request.user
            if user.balance < amount:
                messages.error(request, "Solde insuffisant pour effectuer ce retrait")
                return redirect('accounts:profile')
            
            # Mettre à jour le solde de l'utilisateur
            user.balance -= amount
            user.save()
            
            messages.success(request, f"Votre retrait de {amount}€ a été effectué avec succès !")
            return redirect('accounts:profile')
            
        except (ValueError, TypeError):
            messages.error(request, "Montant invalide")
            return redirect('accounts:profile')
    
    return redirect('accounts:profile')

# def leaderboard(request):
#     users = Utilisateur.objects.annotate(
#         total_bets=Count('bets'),
#         won_bets=Count(
#             Case(
#                 When(bets__status='won', then=Value(1)),
#                 output_field=IntegerField(),
#             )
#         ),
#         total_winnings=Sum(
#             Case(
#                 When(
#                     bets__status='won',
#                     then=ExpressionWrapper(
#                         F('bets__amount') * F('bets__odds'),
#                         output_field=DecimalField(max_digits=10, decimal_places=2)
#                     )
#                 ),
#                 default=Value(Decimal('0')),
#                 output_field=DecimalField(max_digits=10, decimal_places=2),
#             )
#         ),
#         total_bet_amount=Sum('bets__amount')
#     ).order_by('-total_winnings')

#     # Calculer le ROI (Return on Investment) pour chaque utilisateur
#     for user in users:
#         if user.total_bet_amount and user.total_bet_amount > Decimal('0'):
#             user.roi = ((user.total_winnings or Decimal('0')) - user.total_bet_amount) / user.total_bet_amount * Decimal('100')
#         else:
#             user.roi = Decimal('0')

#     context = {
#         'users': users,
#     }
#     return render(request, 'accounts/leaderboard.html', context)
