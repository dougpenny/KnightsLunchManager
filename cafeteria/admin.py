#
# admin.py
#
# Copyright (c) 2024 Doug Penny
# Licensed under MIT
#
# See LICENSE.md for license information
#
# SPDX-License-Identifier: MIT
#


from django.contrib import admin

from rest_framework.authtoken.admin import TokenAdmin
from solo.admin import SingletonModelAdmin

from cafeteria.models import GradeLevel, LunchPeriod, School, Weekday, SiteConfiguration


TokenAdmin.raw_id_fields = ["user"]


@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    fields = ["display_name", "value", "lunch_period", "school"]
    list_filter = ["school", "lunch_period"]
    list_display = ("__str__", "value", "school")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LunchPeriod)
class LunchPeriodAdmin(admin.ModelAdmin):
    fields = [
        "display_name",
        "floating_staff",
        "start_time",
        "teacher_distributes",
        "sort_order",
    ]
    list_display = ("__str__", "start_time", "floating_staff", "teacher_distributes")


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    fields = ["display_name", "active", "name", "school_number"]
    readonly_fields = ["name", "school_number"]
    list_filter = ["active"]
    list_display = ("__str__", "school_number", "active")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Weekday)
class WeekdayAdmin(admin.ModelAdmin):
    fields = ["name", "abbreviation"]
    list_display = ["name", "abbreviation"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(SiteConfiguration, SingletonModelAdmin)
