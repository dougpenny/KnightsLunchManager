from django import forms

from menu.models import MenuItem
from profiles.models import Profile


class ItemOrderForm(forms.Form):
    menu_item = forms.ModelChoiceField(queryset=MenuItem.objects.all(),
        widget=forms.Select(
            attrs={'class': 'block pl-2 pr-10 text-base leading-none text-gray-800 border-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md'}
        )
    )


class TransacteeSelectField(forms.Field):
    def clean(self, value):
        if value:
            profile = Profile.objects.get(user__id=value)
            if profile:
                return profile
            else:
                return None
        else:
            return None


class TransactionDepositForm(forms.Form):
    CASH = 'CASH'
    CHECK = 'CHECK'
    NRCA = 'NRCA'
    NRCA_TRANS = 'NRCA_TRANS'
    ONLINE = 'ONLINE'
    TRANS = 'TRANS'
    DEPOSIT_TYPE_CHOICES = [
        (None, '--------'),
        (CASH, 'Cash'),
        (CHECK, 'Check'),
        (NRCA, 'NRCA Funds'),
        (NRCA_TRANS, 'NRCA Transfer'),
        (ONLINE, 'Online'),
        (TRANS, 'Sibling Transfer'),
    ]
    transactee = TransacteeSelectField(
        widget=forms.Select(attrs={'class': 'transactee-select-ajax', 'style': 'width: 100%'})
    )
    deposit_type = forms.ChoiceField(choices=DEPOSIT_TYPE_CHOICES,
        widget=forms.Select(
            attrs={'class': 'block pr-10 py-1.5 text-base leading-none text-gray-800 border-gray-300 focus:ring-blue-500 focus:border-blue-500 rounded-md'}
        )
    )
    ref = forms.CharField(empty_value=None, required=False,
        widget=forms.TextInput(
            attrs={'class': 'shadow-sm py-1 w-full focus:ring-blue-500 focus:border-blue-500 block sm:text-sm border-gray-300 rounded-md'}
        )
    )
    amount = forms.DecimalField(decimal_places=2,
        widget=forms.NumberInput(
            attrs={'class': 'shadow-sm pl-7 py-1 w-1/2 focus:ring-blue-500 focus:border-blue-500 block sm:text-sm border-gray-300 rounded-md', 'placeholder': '0.00'}
        )
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
