from django import forms

from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'transactee',
            'menut_items',
            'description',
            'amount',
        ]