# Generated by Django 5.2.1 on 2025-05-15 20:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0005_alter_bet_options_alter_match_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='result',
            field=models.CharField(choices=[('home_win', 'Victoire domicile'), ('draw', 'Match nul'), ('away_win', 'Victoire extérieur'), ('pending', 'En attente')], default='pending', max_length=20),
        ),
    ]
