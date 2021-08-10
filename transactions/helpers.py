from django.utils import timezone

from transactions.forms import TransactionDepositForm
from transactions.models import Transaction


def create_deposit(deposit: dict) -> None:
    try:
        profile = deposit['transactee']
        new_balance = profile.current_balance + deposit['amount']
        description = ''
        if deposit['deposit_type'] == TransactionDepositForm.CASH:
            description = 'Cash Deposit'
        elif deposit['deposit_type'] == TransactionDepositForm.CHECK:
            description = 'Check #' + deposit['ref']
        elif deposit['deposit_type'] == TransactionDepositForm.ONLINE:
            description = 'Online Transaction #' + deposit['ref']
        elif deposit['deposit_type'] == TransactionDepositForm.TRANS:
            description = 'Sibling Transfer'
        transaction_type = Transaction.CREDIT
        if deposit['amount'] < 0:
            transaction_type = Transaction.DEBIT
        transaction = Transaction(
            amount=abs(deposit['amount']),
            beginning_balance=profile.current_balance,
            completed=timezone.now(),
            description=description,
            ending_balance=new_balance,
            submitted=timezone.now(),
            transaction_type=transaction_type,
            transactee=profile,
        )
        transaction.save()
        profile.current_balance = new_balance
        profile.save()
    except:
        raise Exception
    
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