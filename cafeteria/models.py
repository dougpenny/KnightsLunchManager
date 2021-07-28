from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models



class GradeLevel(models.Model):
    display_name = models.CharField(blank=True, max_length=24)
    id = models.IntegerField(primary_key=True)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='grades')
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
    pass


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
