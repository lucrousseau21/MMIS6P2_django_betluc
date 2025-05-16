from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('teams', '0006_match_result'),
    ]

    operations = [
        # 1. Ajouter le nouveau champ ForeignKey (null=True pour permettre la transition)
        migrations.AddField(
            model_name='team',
            name='league_new',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='teams',
                to='teams.league',
                verbose_name='Ligue'
            ),
        ),
    ] 