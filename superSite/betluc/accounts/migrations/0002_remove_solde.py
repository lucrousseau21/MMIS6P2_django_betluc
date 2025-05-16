from django.db import migrations, models

def transfer_solde_to_balance(apps, schema_editor):
    Utilisateur = apps.get_model('accounts', 'Utilisateur')
    for user in Utilisateur.objects.all():
        # Si l'utilisateur a un solde > 0, on le transfère
        if user.solde > 0:
            user.balance = user.solde
        else:
            # Sinon on met le solde par défaut de 100€
            user.balance = 100.00
        user.save(update_fields=['balance'])

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(transfer_solde_to_balance),
        migrations.RemoveField(
            model_name='utilisateur',
            name='solde',
        ),
    ] 