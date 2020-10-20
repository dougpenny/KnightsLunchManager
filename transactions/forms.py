from django import forms

from transactions.models import Transaction, MenuLineItem


class TransactionDepositForm(forms.Form):
    transactee = forms.CharField(
        widget=forms.HiddenInput()
    )
    check_num = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'border border-gray-400 py-2 px-2 text-xs rounded-sm block w-full transition duration-150 ease-in-out'}),
        required=False
    )
    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'border border-gray-400 py-2 px-2 text-xs rounded-sm block w-full transition duration-150 ease-in-out'})
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


DepositFormSet = forms.formset_factory(
    TransactionDepositForm,
    extra=25
)