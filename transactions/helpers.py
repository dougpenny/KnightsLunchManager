from collections import Counter

from django.utils import timezone

from menu.models import MenuItem
from profiles.models import Profile
from transactions.forms import TransactionDepositForm
from transactions.models import MenuLineItem, Transaction


def create_deposit(deposit: dict) -> Transaction:
    try:
        profile = deposit["transactee"]
        description = ""
        if deposit["deposit_type"] == TransactionDepositForm.CASH:
            description = "Cash Deposit"
        elif deposit["deposit_type"] == TransactionDepositForm.CHECK:
            description = "Check #" + deposit["ref"] if deposit["ref"] else ""
        elif deposit["deposit_type"] == TransactionDepositForm.NRCA:
            description = "NRCA Provided Funds"
        elif deposit["deposit_type"] == TransactionDepositForm.NRCA_TRANS:
            description = "Transfer of NRCA Funds"
        elif deposit["deposit_type"] == TransactionDepositForm.ONLINE:
            description = (
                "Online Transaction #" + deposit["ref"] if deposit["ref"] else ""
            )
        elif deposit["deposit_type"] == TransactionDepositForm.TRANS:
            description = "Sibling Transfer"
        transaction_type = Transaction.CREDIT
        if deposit["amount"] < 0:
            transaction_type = Transaction.DEBIT
        transaction = Transaction(
            amount=abs(deposit["amount"]),
            beginning_balance=profile.current_balance,
            completed=timezone.now(),
            description=description,
            submitted=timezone.now(),
            transaction_type=transaction_type,
            transactee=profile,
        )
        transaction.save()
        return transaction
    except:
        raise Exception


def create_order(order: dict) -> Transaction:
    try:
        profile = Profile.objects.get(id=order["transactee"])
        new_order = Transaction(
            submitted=timezone.now(),
            transactee=profile,
            transaction_type=Transaction.DEBIT,
        )
        new_order.save()
        description = ""
        cost = 0
        item_counts = Counter(order["items"])
        for menu_item in item_counts:
            item = MenuItem.objects.get(id=menu_item)
            quantity = item_counts[menu_item]
            if description:
                description = description + ", "
            description = description + "({}) {}".format(quantity, item.name)
            cost = cost + (item.cost * quantity)
            menu_line_item = MenuLineItem.objects.create(
                menu_item=item, transaction=new_order, quantity=quantity
            )
            menu_line_item.save()
        new_order.description = description
        new_order.amount = cost
        new_order.save()

        if "temp_trans" in order:
            try:
                old_order = Transaction.objects.get(id=order["temp_trans"])
                old_order.delete()
            except:
                # A previous transaction matching this ID was not found.
                # Why would we recevie a transaction ID for an order that doesn't exist?
                pass
        return new_order
    except:
        raise Exception


def process_transaction(transaction: Transaction):
    try:
        transactee = transaction.transactee
        transaction.beginning_balance = transactee.current_balance
        if transaction.transaction_type == Transaction.CREDIT:
            transaction.ending_balance = transactee.current_balance + transaction.amount
        else:
            transaction.ending_balance = transactee.current_balance - abs(
                transaction.amount
            )
        transaction.completed = timezone.now()
        transaction.save()
        transactee.current_balance = transaction.ending_balance
        transactee.save()
    except:
        raise Exception
