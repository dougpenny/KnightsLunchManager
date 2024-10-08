from datetime import time

from django.db import models
from solo.models import SingletonModel


class GradeLevel(models.Model):
    display_name = models.CharField(blank=True, max_length=24)
    lunch_period = models.ForeignKey(
        "LunchPeriod",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="grades",
    )
    school = models.ForeignKey(
        "School",
        on_delete=models.CASCADE,
        limit_choices_to={"active": True},
        related_name="grades",
    )
    value = models.SmallIntegerField(unique=True)

    def __str__(self):
        if self.display_name != "":
            return self.display_name
        else:
            return str(self.value)

    class Meta:
        ordering = ["value"]
        verbose_name_plural = "Grade Levels"


class LunchPeriod(models.Model):
    display_name = models.CharField(blank=True, max_length=24)
    floating_staff = models.BooleanField(
        default=False,
        help_text="Floating period for staff without a homeroom.",
        verbose_name="floating staff period",
    )
    start_time = models.TimeField(blank=True, null=True)
    sort_order = models.SmallIntegerField(
        default=0, help_text="Order in which the lunch period will be displayed"
    )
    teacher_distributes = models.BooleanField(
        default=False, help_text="Does the teacher distribute orders for their class?"
    )

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ["sort_order", "start_time"]
        verbose_name_plural = "Lunch Periods"


class School(models.Model):
    active = models.BooleanField(
        default=False, help_text="Should this school be included when syncing students?"
    )
    display_name = models.CharField(blank=True, max_length=100)
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    school_number = models.IntegerField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        if self.display_name != "":
            return self.display_name
        else:
            return self.name


class Weekday(models.Model):
    abbreviation = models.CharField(max_length=3)
    name = models.CharField(max_length=12)

    def __str__(self):
        return self.name


class SiteConfiguration(SingletonModel):
    balance_export_path = models.CharField(
        blank=True,
        help_text="File path to which current balance export files should be saved.",
        max_length=255,
    )
    closed_for_break = models.BooleanField(
        default=False,
        help_text="Is the cafeteria closed for a school break or holiday?",
    )
    closed_message = models.CharField(
        blank=True,
        help_text="The message to be displayed with the cafeteria is closed for a break or holiday.",
    )
    current_year = models.CharField(help_text="The current school year.", max_length=10)
    debt_limit = models.FloatField(
        default=0.00,
        help_text="The debt limit at which point users are prevented from ordering.",
    )
    new_card_fee = models.FloatField(
        default=0.00, help_text="The fee charged for a new lunch card."
    )
    order_close_time = models.TimeField(
        default=time(8, 15), help_text="The time orders should stop being accepted."
    )
    order_open_time = models.TimeField(
        default=time(0, 0), help_text="The time orders should start being accepted."
    )
    reports_email = models.CharField(
        blank=True,
        help_text="The email addresses, comma seperated, to which system reports should be sent.",
    )

    def __str__(self):
        return "Site Configuration"

    class Meta:
        verbose_name = "Site Configuration"
