from django import forms

from .models import Transaction


class TransactionForm(forms.Form):
    transactee = forms.CharField()
    amount = forms.DecimalField()
    transaction_type = forms.CharField()
    description = forms.TextInput()
    menu_items = forms.CharField()
    submitted = forms.DateTimeField()
    completed = forms.DateTimeField()
