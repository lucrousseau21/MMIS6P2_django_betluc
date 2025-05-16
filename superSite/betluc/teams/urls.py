from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    # Ligues
    path('leagues/', views.league_list, name='league_list'),
    
    # Équipes
    path('teams/', views.team_list, name='team_list'),
    path('leagues/<int:league_id>/teams/', views.team_list, name='league_teams'),
    path('teams/<int:team_id>/', views.team_detail, name='team_detail'),
    
    # Journées
    path('leagues/<int:league_id>/matchdays/', views.matchday_list, name='matchday_list'),
    path('matchdays/<int:matchday_id>/', views.matchday_detail, name='matchday_detail'),
    path('matchdays/', views.matchdays_grid, name='matchdays_grid'),
    
    # Matchs
    path('matches/', views.match_list, name='match_list'),
    path('leagues/<int:league_id>/matches/', views.match_list, name='league_matches'),
    path('matches/<int:match_id>/', views.match_detail, name='match_detail'),
    
    # Paris
    path('matches/<int:match_id>/bet/', views.place_bet, name='place_bet'),
    path('my-bets/', views.my_bets, name='my_bets'),
] 