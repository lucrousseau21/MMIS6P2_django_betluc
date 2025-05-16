from django.core.management.base import BaseCommand
from teams.models import League, Team

class Command(BaseCommand):
    help = 'Charge les équipes de Ligue 1 dans la base de données'

    def handle(self, *args, **options):
        # Création de la Ligue 1
        ligue1, created = League.objects.get_or_create(
            name="Ligue 1",
            defaults={
                'country': 'France'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Ligue 1 créée avec succès'))
        else:
            self.stdout.write(self.style.WARNING('Ligue 1 existe déjà, utilisation de l\'existante'))
        
        # Liste des équipes de Ligue 1
        teams_data = [
            {"name": "Paris Saint-Germain", "city": "Paris", "stadium": "Parc des Princes"},
            {"name": "Olympique de Marseille", "city": "Marseille", "stadium": "Stade Vélodrome"},
            {"name": "AS Monaco", "city": "Monaco", "stadium": "Stade Louis II"},
            {"name": "OGC Nice", "city": "Nice", "stadium": "Allianz Riviera"},
            {"name": "LOSC Lille", "city": "Lille", "stadium": "Stade Pierre-Mauroy"},
            {"name": "RC Strasbourg", "city": "Strasbourg", "stadium": "Stade de la Meinau"},
            {"name": "Olympique Lyonnais", "city": "Lyon", "stadium": "Groupama Stadium"},
            {"name": "Stade Brestois 29", "city": "Brest", "stadium": "Stade Francis-Le Blé"},
            {"name": "RC Lens", "city": "Lens", "stadium": "Stade Bollaert-Delelis"},
            {"name": "AJ Auxerre", "city": "Auxerre", "stadium": "Stade de l'Abbé-Deschamps"},
            {"name": "Stade Rennais", "city": "Rennes", "stadium": "Roazhon Park"},
            {"name": "Toulouse FC", "city": "Toulouse", "stadium": "Stadium de Toulouse"},
            {"name": "Angers SCO", "city": "Angers", "stadium": "Stade Raymond Kopa"},
            {"name": "Stade de Reims", "city": "Reims", "stadium": "Stade Auguste-Delaune"},
            {"name": "FC Nantes", "city": "Nantes", "stadium": "Stade de la Beaujoire"},
            {"name": "Le Havre AC", "city": "Le Havre", "stadium": "Stade Océane"},
            {"name": "AS Saint-Étienne", "city": "Saint-Étienne", "stadium": "Stade Geoffroy-Guichard"},
            {"name": "Montpellier HSC", "city": "Montpellier", "stadium": "Stade de la Mosson"}
        ]
        
        # Création des équipes
        teams_created = 0
        teams_existing = 0
        
        for team_data in teams_data:
            team, created = Team.objects.get_or_create(
                name=team_data["name"],
                defaults={
                    'league': ligue1,
                    'city': team_data["city"],
                    'stadium': team_data["stadium"]
                }
            )
            
            if created:
                teams_created += 1
            else:
                teams_existing += 1
        
        self.stdout.write(self.style.SUCCESS(f'Équipes créées: {teams_created}'))
        self.stdout.write(self.style.WARNING(f'Équipes existantes: {teams_existing}')) 