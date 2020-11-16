import os

from datetime import date, datetime, time

from django.db import models
from django.urls import reverse
from django.utils import timezone


class MenuLineItem(models.Model):
    menu_item = models.ForeignKey(
        'menu.MenuItem', on_delete=models.CASCADE, related_name='line_item')
    transaction = models.ForeignKey(
        'Transaction', on_delete=models.CASCADE, related_name='line_item')
    quantity = models.SmallIntegerField()

    def __str__(self):
        return str(self.quantity) + ' - ' + self.menu_item.name


class Transaction(models.Model):
    DEBIT = 'DB'
    CREDIT = 'CR'
    TYPE_CHOICES = [
        (DEBIT, 'Debit'),
        (CREDIT, 'Credit'),
    ]
    amount = models.DecimalField(decimal_places=2, default=0, max_digits=6)
    beginning_balance = models.DecimalField(
        decimal_places=2, max_digits=6, null=True)
    completed = models.DateTimeField(blank=True, default=None, null=True)
    description = models.TextField(blank=True, default='')
    menu_items = models.ManyToManyField(
        'menu.MenuItem', blank=True, related_name='transactions', through=MenuLineItem)
    ending_balance = models.DecimalField(
        decimal_places=2, max_digits=6, null=True)
    ps_transaction_id = models.IntegerField(blank=True, default=None, null=True)
    submitted = models.DateTimeField(default=timezone.now)
    transaction_type = models.CharField(
        choices=TYPE_CHOICES, default=DEBIT, max_length=2)
    transactee = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE)

    class Meta:
        ordering = ['submitted']

    def get_absolute_url(self):
        return reverse('transactions:transaction-detail', kwargs={'pk': self.pk})

    @property
    def status(self):
        midnight_today = timezone.make_aware(
            datetime.combine(date.today(), time(0, 0)))
        cutoff_time = datetime.time(datetime.strptime(
            os.getenv('ORDER_CUTOFF'), '%H:%M'))
        cutoff_today = timezone.make_aware(
            datetime.combine(date.today(), cutoff_time))
        if self.completed:
            return 'Complete'
        elif self.submitted > midnight_today and timezone.now() < cutoff_today:
            return 'Submitted'
        else:
            return 'Processing'

    @staticmethod
    def accepting_orders() -> bool:
        cutoff_time = datetime.time(datetime.strptime(
            os.getenv('ORDER_CUTOFF'), '%H:%M'))
        return cutoff_time > datetime.now().time()
