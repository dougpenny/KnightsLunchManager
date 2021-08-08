from django import forms

from cafeteria.models import School
from menu.models import MenuItem


class GeneralForm(forms.Form):
    open_time = forms.TimeField(required=False, widget=forms.TimeInput(format='%H:%M', attrs={
        'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md',
        'type': 'time', 'disabled': 'true'}))
    close_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={
        'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md',
        'type': 'time'}))
    closed_for_summer = forms.NullBooleanField(widget=forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No'),]))
    reports_email = forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'text',
        'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md'}))
    balance_export_path = forms.CharField(widget=forms.TextInput(attrs={'type': 'text',
        'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md'}))
    current_year = forms.CharField(required=False, widget=forms.TextInput(attrs={'type': 'text',
        'class': 'shadow-sm focus:ring-blue-500 focus:border-blue-500 block sm:text-sm border-gray-300 rounded-md'}))
    new_card_fee = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'type': 'number',
        'class': 'shadow-sm pl-7 focus:ring-blue-500 focus:border-blue-500 block sm:text-sm border-gray-300 rounded-md',
        'placeholder': '0.00'}), decimal_places=2)


class SchoolsModelForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ('active', 'display_name', 'name')
        widgets = {
            'active': forms.CheckboxInput(attrs={
                'class': 'focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded'
            }),
            'display_name': forms.TextInput(attrs={
                'class': 'mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'
            }),
            'name': forms.HiddenInput(attrs={'readonly': 'True'})
        }


class MenuItemChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return '{} - ${}'.format(obj.name, obj.cost)


class UserOrderForm(forms.Form):
    menu_item = MenuItemChoiceField(queryset=MenuItem.objects.all(), widget=forms.Select(attrs={
        'class': 'block pl-3 pr-10 py-2 text-sm border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md'}))
    def __init__(self, *args, **kwargs):
        queryset = kwargs.pop('queryset', None)
        super(UserOrderForm, self).__init__(*args, **kwargs)
        if queryset:
            self.fields['menu_item'].queryset = queryset
