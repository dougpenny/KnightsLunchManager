from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from menu.models import MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "name",
                    "short_name",
                    "description",
                    "cost",
                    "category",
                    "sequence",
                ]
            },
        ),
        ("Pizza", {"fields": ["pizza", "slices_per"]}),
        ("Limited Item", {"fields": ["limited", "max_num"]}),
        ("Availability", {"fields": ["days_available", "lunch_period", "app_only"]}),
    ]
    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple},
    }
    list_display = ("name", "short_name", "sequence", "cost", "limited", "max_num")
    list_filter = ["days_available", "lunch_period", "limited"]
