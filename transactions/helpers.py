from django.utils import timezone

from transactions.models import Transaction


def process_order(order: Transaction):
    try:
        transactee = order.transactee
        order.beginning_balance = transactee.current_balance
        order.ending_balance = transactee.current_balance - order.amount
        order.completed = timezone.now()
        order.save()
        transactee.current_balance = order.ending_balance
        transactee.save()
    except:
        raise Exception