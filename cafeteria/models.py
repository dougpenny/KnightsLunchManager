from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models



class GradeLevel(models.Model):
    display_name = models.CharField(blank=True, max_length=24)
    lunch_period = models.ForeignKey('LunchPeriod', on_delete=models.SET_NULL, blank=True, null=True, related_name='grades')
    school = models.ForeignKey('School', on_delete=models.CASCADE, limit_choices_to={'active': True}, related_name='grades')
    value = models.SmallIntegerField(unique=True)

    def __str__(self):
        if self.display_name != '':
            return self.display_name
        else:
            return str(self.value)

    class Meta:
        ordering = ['value']
        verbose_name_plural = 'Grade Levels'


class LunchPeriod(models.Model):
    display_name = models.CharField(blank=True, max_length=24)
    start_time = models.TimeField(blank=True, null=True)
    teacher_distributes = models.BooleanField(default=False, help_text='Does the teacher distribute orders for their class?')

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ['start_time']
        verbose_name_plural = 'Lunch Periods'


class School(models.Model):
    active = models.BooleanField(
        default=False, help_text='Should this school be included when syncing students?')
    display_name = models.CharField(blank=True, max_length=100)
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    school_number = models.IntegerField()

    class Meta:
        ordering = ['name']


    def __str__(self):
        if self.display_name != '':
            return self.display_name
        else:
            return self.name


class Weekday(models.Model):
    abbreviation = models.CharField(max_length=3)
    name = models.CharField(max_length=12)

    def __str__(self):
        return self.name
