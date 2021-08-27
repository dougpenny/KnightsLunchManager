from django.db import models


class MenuItem(models.Model):
    ENTREE = 'ENT'
    SIDE = 'SIDE'
    DESSERT = 'DEST'
    DRINK = 'DRINK'
    CATEGORY_CHOICES = [
        (ENTREE, 'Entree'),
        (SIDE, 'Side'),
        (DESSERT, 'Dessert'),
        (DRINK, 'Drink'),
    ]
    app_only = models.BooleanField(default=False, verbose_name='à la carte only')
    cost = models.DecimalField(decimal_places=2, max_digits=6)
    category = models.CharField(
        choices=CATEGORY_CHOICES, default='', max_length=6)
    days_available = models.ManyToManyField(
        'cafeteria.Weekday',
        blank=True,
        related_name='menu_items'
    )
    description = models.TextField(blank=True, default='')
    lunch_period = models.ManyToManyField(
        'cafeteria.LunchPeriod',
        blank=True,
        help_text='Choose lunch period availability',
        related_name='menu_items',
        verbose_name='lunch periods available'
    )
    name = models.CharField(
        help_text='Will be displayed to students',
        max_length=100
    )
    pizza = models.BooleanField(default=False, verbose_name='Pizza?')
    slices_per = models.SmallIntegerField(default=0, verbose_name='Slices per pizza')
    sequence = models.SmallIntegerField(
        help_text='Order item will appear in menu')
    short_name = models.CharField(
        help_text='Will be used on reports to quickly identify the item',
        max_length=20,
        blank=True
    )

    class Meta:
        ordering = ['sequence']
        verbose_name_plural = 'Menu Items'

    def __str__(self):
        return self.name
