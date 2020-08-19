from django.db import models


class MenuItem(models.Model):
    ENTREE = 'ENT'
    SIDE = 'SIDE'
    DRINK = 'DRINK'
    CATEGORY_CHOICES = [
        (ENTREE, 'Entree'),
        (SIDE, 'Side'),
        (DRINK, 'Drink'),
    ]
    cost = models.DecimalField(decimal_places=2, max_digits=6)
    category = models.CharField(choices=CATEGORY_CHOICES, default='', max_length=6)
    days_available = models.ManyToManyField(
        'cafeteria.Weekday',
        blank=True,
        related_name='menu_items'
    )
    description = models.TextField(blank=True, default='')
    schools_available = models.ManyToManyField(
        'cafeteria.School',
        blank=True,
        help_text='Choose school availability',
        related_name='menu_items'
    )
    name = models.CharField(
        help_text='Will be displayed to students',
        max_length=100
    )
    sequence = models.SmallIntegerField(help_text='Order item will appear in menu')
    short_name = models.CharField(
        help_text='Will be used on reports to quickly identify the item',
        max_length=10,
        blank=True
    )

    class Meta:
        ordering = ['sequence']
        verbose_name_plural = 'Menu Items'

    def __str__(self):
        return self.name
