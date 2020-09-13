from django import forms

from .models import Transaction, MenuLineItem


class TransactionForm(forms.ModelForm):
    #transactee = forms.CharField()
    amount = forms.DecimalField(
        widget=forms.NumberInput(attrs={'class': 'form-input block w-full transition duration-150 ease-in-out sm:text-sm sm:leading-5'})
    )
    transaction_type = forms.ChoiceField(
        choices=Transaction.TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select block w-full transition duration-150 ease-in-out sm:text-sm sm:leading-5'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-input block w-full transition duration-150 ease-in-out sm:text-sm sm:leading-5'})
    )
    #menu_items = forms.CharField()
    submitted = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'class': 'form-input block w-full transition duration-150 ease-in-out sm:text-sm sm:leading-5'})
    )

    class Meta:
        model = Transaction
        fields = ['transactee', 'amount', 'transaction_type', 'description', 'menu_items', 'submitted']


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

DepositFormSet = forms.formset_factory(
    TransactionDepositForm,
    extra=25
)


class TransactionOrderForm(forms.Form):
    transactee = forms.CharField(
        widget=forms.HiddenInput()
    )

MenuLineItemFormSet = forms.inlineformset_factory(
    Transaction,
    MenuLineItem,
    can_delete=True,
    max_num=1,
    fields=('menu_item', 'quantity'),
    widgets={
        'menu_item': forms.Select(attrs={'class': 'border border-gray-400 py-2 px-2 text-xs rounded-sm block w-full transition duration-150 ease-in-out'}),
        'quantity': forms.NumberInput(attrs={'class': 'border border-gray-400 py-2 px-2 text-xs rounded-sm block w-full transition duration-150 ease-in-out'}),
    }
)