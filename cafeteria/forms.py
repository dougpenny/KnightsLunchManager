from django.forms import ModelForm, CheckboxInput, HiddenInput, TextInput

from cafeteria.models import School


class SchoolsModelForm(ModelForm):
    class Meta:
        model = School
        fields = ('active', 'display_name', 'name')
        widgets = {
            'active': CheckboxInput(attrs={'class': 'focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded'}),
            'display_name': TextInput(attrs={'class': 'mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'}),
            'name': HiddenInput(attrs={'readonly': 'True'})
        }