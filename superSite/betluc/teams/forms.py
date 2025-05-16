from django import forms
from decimal import Decimal
from .models import Bet

class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ['bet_type', 'amount']
        widgets = {
            'bet_type': forms.RadioSelect,
            'amount': forms.NumberInput(attrs={'min': '1', 'step': '1'})
        }
        labels = {
            'bet_type': 'Type de pari',
            'amount': 'Montant (€)'
        }
    
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount < Decimal('1.00'):
            raise forms.ValidationError("Le montant minimum est de 1€.")
        if amount > Decimal('1000.00'):
            raise forms.ValidationError("Le montant maximum est de 1000€.")
        return amount 