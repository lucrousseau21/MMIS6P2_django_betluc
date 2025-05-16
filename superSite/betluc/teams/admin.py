from django.contrib import admin
from .models import League, Team, Matchday, Match, Odds, Bet

@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name', 'country')

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'league', 'city', 'stadium')
    list_filter = ('league',)
    search_fields = ('name', 'city', 'stadium')

@admin.register(Matchday)
class MatchdayAdmin(admin.ModelAdmin):
    list_display = ('league', 'number', 'date', 'is_completed')
    list_filter = ('league', 'is_completed')
    search_fields = ('league__name',)
    ordering = ('-date', 'league', 'number')

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('home_team', 'away_team', 'matchday', 'date', 'home_score', 'away_score', 'result', 'status', 'stadium')
    list_filter = ('status', 'result', 'matchday__league')
    search_fields = ('home_team__name', 'away_team__name', 'stadium')
    ordering = ('-date',)
    
    actions = ['update_match_results']
    
    def update_match_results(self, request, queryset):
        for match in queryset:
            match.update_result()
        self.message_user(request, f"{queryset.count()} match(s) mis à jour.")
    update_match_results.short_description = "Mettre à jour les résultats des matchs sélectionnés"

@admin.register(Odds)
class OddsAdmin(admin.ModelAdmin):
    list_display = ('match', 'home_win', 'draw', 'away_win')
    search_fields = ('match__home_team__name', 'match__away_team__name')

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'bet_type', 'amount', 'odds', 'status', 'created_at')
    list_filter = ('status', 'bet_type', 'created_at')
    search_fields = ('user__username', 'match__home_team__name', 'match__away_team__name')
    ordering = ('-created_at',)
