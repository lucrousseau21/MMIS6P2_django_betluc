from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Max
from django.http import HttpResponseForbidden
from .models import League, Team, Matchday, Match, Odds, Bet
from .forms import BetForm

def get_next_matchday(league=None):
    """Récupère la première journée non terminée"""
    query = Matchday.objects.filter(
        is_completed=False
    ).order_by('date')
    
    if league:
        query = query.filter(league=league)
    
    return query.first()

def league_list(request):
    leagues = League.objects.all()
    return render(request, 'teams/league_list.html', {'leagues': leagues})

def team_list(request, league_id=None):
    if league_id:
        league = get_object_or_404(League, id=league_id)
        teams = Team.objects.filter(league=league)
        context = {
            'league': league,
            'teams': teams
        }
    else:
        teams = Team.objects.all()
        context = {
            'teams': teams
        }
    return render(request, 'teams/team_list.html', context)

def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    # Récupérer les matchs à venir de l'équipe
    upcoming_matches = Match.objects.filter(
        Q(home_team=team) | Q(away_team=team),
        date__gt=timezone.now(),
        status='scheduled'
    ).order_by('date')[:5]
    
    # Récupérer les derniers matchs de l'équipe
    past_matches = Match.objects.filter(
        Q(home_team=team) | Q(away_team=team),
        date__lt=timezone.now(),
        status='completed'
    ).order_by('-date')[:5]
    
    return render(request, 'teams/team_detail.html', {
        'team': team,
        'upcoming_matches': upcoming_matches,
        'past_matches': past_matches
    })

def matchday_list(request, league_id):
    league = get_object_or_404(League, id=league_id)
    matchdays = Matchday.objects.filter(league=league).order_by('number')
    return render(request, 'teams/matchday_list.html', {
        'league': league,
        'matchdays': matchdays
    })

def matchday_detail(request, matchday_id):
    matchday = get_object_or_404(Matchday, id=matchday_id)
    matches = Match.objects.filter(matchday=matchday).order_by('date')
    return render(request, 'teams/matchday_detail.html', {
        'matchday': matchday,
        'matches': matches
    })

def match_list(request, league_id=None):
    # Récupérer la prochaine journée
    league = None
    if league_id:
        league = get_object_or_404(League, id=league_id)
    
    leagues = League.objects.all()
    next_matchday = get_next_matchday(league)
    
    # Récupérer les matchs à venir
    if next_matchday:
        upcoming_matches = Match.objects.filter(
            matchday=next_matchday,
            status='scheduled'
        ).order_by('date')
        
        # Récupérer les matchs en cours
        in_progress_matches = Match.objects.filter(
            matchday=next_matchday,
            status='live'
        ).order_by('date')
        
        # Récupérer les matchs terminés de la journée en cours
        completed_matches_current = Match.objects.filter(
            matchday=next_matchday,
            status='completed'
        ).order_by('date')
        
        # Récupérer les derniers matchs terminés des journées précédentes
        last_completed_matchday = Matchday.objects.filter(
            league=league if league else None,
            is_completed=True,
            date__lt=next_matchday.date
        ).order_by('-date').first()
        
        if last_completed_matchday:
            recent_matches = Match.objects.filter(
                matchday=last_completed_matchday,
                status='completed'
            ).order_by('date')
        else:
            recent_matches = Match.objects.none()
    else:
        upcoming_matches = Match.objects.none()
        in_progress_matches = Match.objects.none()
        completed_matches_current = Match.objects.none()
        recent_matches = Match.objects.none()
        last_completed_matchday = None
    
    # Récupérer toutes les journées terminées avec leurs matchs
    completed_matchdays = Matchday.objects.filter(
        league=league if league else None,
        is_completed=True
    ).order_by('-date')
    
    completed_matchdays_data = []
    for matchday in completed_matchdays:
        # Ne pas ajouter la dernière journée terminée si elle est déjà affichée
        if last_completed_matchday and matchday.id == last_completed_matchday.id:
            continue
            
        matches = Match.objects.filter(
            matchday=matchday,
            status='completed'
        ).order_by('date')
        if matches.exists():
            completed_matchdays_data.append({
                'matchday': matchday,
                'matches': matches
            })
    
    return render(request, 'teams/match_list.html', {
        'league': league,
        'leagues': leagues,
        'next_matchday': next_matchday,
        'upcoming_matches': upcoming_matches,
        'in_progress_matches': in_progress_matches,
        'completed_matches_current': completed_matches_current,
        'recent_matches': recent_matches,
        'completed_matchdays_data': completed_matchdays_data
    })

@login_required
def match_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    
    # Vérifier si le match a des cotes
    try:
        odds = match.odds
    except Odds.DoesNotExist:
        odds = Odds.create_for_match(match)
    
    # Si l'utilisateur est connecté, lui permettre de parier
    user_bet = None
    if request.user.is_authenticated:
        # Vérifier si l'utilisateur a déjà parié sur ce match
        user_bet = Bet.objects.filter(user=request.user, match=match).first()
    
    # Si le match est programmé, permettre les paris
    can_bet = match.status == 'scheduled'
    
    if request.method == 'POST' and can_bet and not user_bet:
        form = BetForm(request.POST)
        if form.is_valid():
            bet = form.save(commit=False)
            bet.user = request.user
            bet.match = match
            bet.odds = odds.get_odds_for_bet_type(bet.bet_type)
            
            # Vérifier si l'utilisateur a suffisamment d'argent
            if request.user.balance < bet.amount:
                messages.error(request, "Vous n'avez pas assez d'argent pour placer ce pari.")
                return redirect('teams:match_detail', match_id=match.id)
            
            # Utiliser une transaction pour s'assurer que tout est cohérent
            from django.db import transaction
            with transaction.atomic():
                # Déduire le montant du pari de la balance
                if request.user.remove_balance(bet.amount):
                    bet.save()
                    messages.success(request, f"Votre pari de {bet.amount}€ a été placé avec succès. Gain potentiel : {bet.potential_win}€")
                else:
                    messages.error(request, "Une erreur est survenue lors du placement du pari.")
            
            return redirect('teams:match_detail', match_id=match.id)
    else:
        form = BetForm()
    
    return render(request, 'teams/match_detail.html', {
        'match': match,
        'odds': odds,
        'form': form,
        'user_bet': user_bet,
        'can_bet': can_bet
    })

@login_required
def place_bet(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    
    # Vérifier si le match est disponible pour les paris
    if match.status != 'scheduled':
        messages.error(request, "Ce match n'est plus disponible pour les paris.")
        return redirect('teams:match_detail', match_id=match_id)
    
    # Vérifier si l'utilisateur a déjà parié sur ce match
    if Bet.objects.filter(user=request.user, match=match).exists():
        messages.error(request, "Vous avez déjà placé un pari sur ce match.")
        return redirect('teams:match_detail', match_id=match_id)
    
    if request.method == 'POST':
        form = BetForm(request.POST)
        if form.is_valid():
            bet_type = form.cleaned_data['bet_type']
            amount = form.cleaned_data['amount']
            
            # Vérifier si l'utilisateur a suffisamment d'argent
            if request.user.balance < amount:
                messages.error(request, "Vous n'avez pas assez d'argent pour placer ce pari.")
                return redirect('teams:match_detail', match_id=match_id)
            
            # Récupérer la cote correspondante
            odds = match.odds
            if bet_type == 'home_win':
                odds_value = odds.home_win
            elif bet_type == 'away_win':
                odds_value = odds.away_win
            else:  # draw
                odds_value = odds.draw
            
            # Créer le pari
            bet = Bet(
                user=request.user,
                match=match,
                bet_type=bet_type,
                amount=amount,
                odds=odds_value
            )
            bet.save()
            
            messages.success(request, f"Votre pari de {amount}€ a été placé avec succès. Gain potentiel : {bet.potential_win}€")
            return redirect('teams:match_detail', match_id=match_id)
    else:
        form = BetForm()
    
    return render(request, 'teams/match_detail.html', {
        'form': form,
        'match': match
    })

@login_required
def user_bets(request):
    # Récupérer tous les paris de l'utilisateur
    bets = Bet.objects.filter(user=request.user).order_by('-created_at')
    
    # Séparer les paris en cours et les paris terminés
    active_bets = bets.filter(status='pending')
    completed_bets = bets.exclude(status='pending')
    
    return render(request, 'teams/user_bets.html', {
        'active_bets': active_bets,
        'completed_bets': completed_bets
    })

def matchdays_grid(request):
    # Récupérer toutes les ligues
    leagues = League.objects.all()
    
    # Créer un dictionnaire pour stocker les données des journées par ligue
    leagues_data = []
    
    for league in leagues:
        # Récupérer les journées avec le nombre de matchs pour cette ligue
        matchdays = Matchday.objects.filter(
            league=league
        ).annotate(
            matches_count=Count('matches')
        ).order_by('number')
        
        # Calculer le nombre maximum de journées pour cette ligue
        max_matchday = matchdays.aggregate(max_number=Max('number'))['max_number'] or 0
        
        leagues_data.append({
            'league': league,
            'matchdays': matchdays,
            'max_matchday': max_matchday
        })
    
    return render(request, 'teams/matchdays_grid.html', {
        'leagues_data': leagues_data,
        'now': timezone.now()
    })

@login_required
def my_bets(request):
    """Affiche l'historique des paris de l'utilisateur"""
    bets = Bet.objects.filter(user=request.user).order_by('-created_at')
    
    # Filtrer par statut si spécifié
    status = request.GET.get('status')
    if status in ['won', 'lost', 'pending']:
        bets = bets.filter(status=status)
    
    context = {
        'bets': bets,
        'total_bets': bets.count(),
        'won_bets': bets.filter(status='won').count(),
        'lost_bets': bets.filter(status='lost').count(),
        'pending_bets': bets.filter(status='pending').count(),
    }
    
    return render(request, 'teams/my_bets.html', context)
