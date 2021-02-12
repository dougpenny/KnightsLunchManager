from powerschool.powerschool import Powerschool
from transactions.models import Transaction


def export_transactions(transactions: [Transaction]) -> int:
    client = Powerschool()
    count: int = 0
    for transaction in transactions:
        transaction_info = {}
        transaction_info['amount'] = str(transaction.amount)
        transaction_info['beginning_balance'] = str(transaction.beginning_balance)
        transaction_info['completed'] = transaction.completed.strftime('%Y-%m-%d')
        transaction_info['description'] = transaction.description
        transaction_info['ending_balance'] = str(transaction.ending_balance)
        transaction_info['submitted'] = transaction.submitted.strftime('%Y-%m-%d')
        transaction_info['transaction_id'] = str(transaction.id)
        transaction_info['transaction_type'] = transaction.transaction_type
        transaction_info['studentsdcid'] = str(transaction.transactee.student_dcid)
        powerschool_id = client.new_lunch_transaction(transaction_info)
        if powerschool_id:
            transaction.ps_transaction_id = powerschool_id
            transaction.save()
            count = count + 1
    return count