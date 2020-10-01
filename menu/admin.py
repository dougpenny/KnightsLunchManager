from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from cafeteria.models import School
from menu.models import MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'short_name', 'description', 'cost', 'category', 'sequence']}),
        ('Availability', {'fields': ['days_available', 'schools_available']})
    ]
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    list_display = ('name', 'short_name', 'sequence', 'cost')
    list_filter = ['days_available', 'schools_available']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'schools_available':
            kwargs["queryset"] = School.objects.filter(active=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)
