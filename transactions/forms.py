from django import forms

from menu.models import MenuItem
from transactions.models import Transaction, MenuLineItem


class TransactionDepositForm(forms.Form):
    transactee = forms.CharField(
        widget=forms.HiddenInput()
    )
    check_num = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'text',
                               'class': 'border border-gray-400 py-2 px-2 text-xs rounded-sm block w-full transition duration-150 ease-in-out'}),
        required=False
    )
    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'type': 'number',
                                 'class': 'border border-gray-400 py-2 px-2 text-xs rounded-sm block w-full transition duration-150 ease-in-out'})
    )
    submitted = forms.DateTimeField(
        required=False,
        widget=forms.HiddenInput()
    )


class TransactionOrderForm(forms.Form):
    transactee = forms.CharField(
        widget=forms.HiddenInput()
    )
    menu_item = forms.CharField(
        widget=forms.HiddenInput()
    )
    submitted = forms.DateTimeField(
        widget=forms.HiddenInput()
    )


class ItemOrderForm(forms.Form):
    menu_item = forms.ModelChoiceField(queryset=MenuItem.objects.all(), widget=forms.Select(attrs={
        'class': 'block pl-2 pr-10 text-base leading-none text-gray-800 border-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md'}))


DepositFormSet = forms.formset_factory(
    TransactionDepositForm,
    extra=25
)
