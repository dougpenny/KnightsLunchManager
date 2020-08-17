from datetime import datetime
import os

from django.db import models


class MenuLineItem(models.Model):
    menu_item = models.ForeignKey('menu.MenuItem', on_delete=models.CASCADE, related_name='line_item')
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, related_name='line_item')
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
    amount = models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)
    beginning_balance = models.DecimalField(decimal_places=2, max_digits=6, null=True)
    completed = models.DateTimeField(blank=True, default=None, null=True)
    description = models.TextField(blank=True, default='')
    menu_items = models.ManyToManyField('menu.MenuItem', blank=True, related_name='transactions',through=MenuLineItem)
    new_balance = models.DecimalField(decimal_places=2, max_digits=6, null=True)
    submitted = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(choices=TYPE_CHOICES, default=DEBIT, max_length=2)
    transactee = models.ForeignKey('profiles.Profile', on_delete=models.CASCADE)

    @property
    def status(self):
        if self.completed:
            return 'Complete'
        elif not self.__class__.accepting_orders():
            return 'Processing'
        elif self.submitted:
            return 'Submitted'
        else:
            return 'Unknown'

    @staticmethod
    def accepting_orders() -> bool:
            time_format = '%H:%M'
            cutoff_time = datetime.time(datetime.strptime(os.getenv('ORDER_CUTOFF'), time_format))
            return cutoff_time > datetime.now().time()