from django.contrib import admin

from cafeteria.models import School
from cafeteria.models import Weekday


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    fields = ['display_name', 'active', 'name', 'school_number']
    readonly_fields = ['name', 'school_number']
    list_filter = ['active']
    list_display = ('__str__', 'school_number', 'active')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Weekday)
class WeekdayAdmin(admin.ModelAdmin):
    fields = ['name', 'abbreviation']
    list_display = ['name', 'abbreviation']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False