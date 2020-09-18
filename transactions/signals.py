from django.db.models.signals import pre_delete
from django.dispatch import receiver

from transactions.models import Transaction
#from profiles.models import Profile


@receiver(pre_delete, sender=Transaction)
def update_balances(sender, instance, **kwargs):
    if instance.completed:
        following_completed = Transaction.objects.filter(
            transactee=instance.transactee,
            completed__gte=instance.completed
        )
        amount = 0
        if instance.transaction_type == Transaction.CREDIT:
            amount = -(instance.amount)
        else:
            amount = instance.amount
        for completed_transaction in following_completed:
            completed_transaction.beginning_balance = completed_transaction.beginning_balance + amount
            completed_transaction.ending_balance = completed_transaction.ending_balance + amount
            completed_transaction.save()
        instance.transactee.current_balance = instance.transactee.current_balance + amount
        instance.transactee.save()
