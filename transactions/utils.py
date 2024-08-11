import os

from typing import List

from pypowerschool import powerschool
from transactions.models import Transaction


def export_transactions(transactions: List[Transaction]) -> int:
    base_url = os.getenv("POWERSCHOOL_URL")
    client_id = os.getenv("POWERSCHOOL_CLIENT_ID")
    client_secret = os.getenv("POWERSCHOOL_CLIENT_SECRET")
    client = powerschool.Client(base_url, client_id, client_secret)
    count: int = 0
    for transaction in transactions:
        if not transaction.ps_transaction_id:
            transaction_info = {}
            transaction_info["amount"] = str(transaction.amount)
            transaction_info["beginning_balance"] = str(transaction.beginning_balance)
            transaction_info["completed"] = transaction.completed.strftime("%Y-%m-%d")
            transaction_info["description"] = transaction.description
            transaction_info["ending_balance"] = str(transaction.ending_balance)
            transaction_info["submitted"] = transaction.submitted.strftime("%Y-%m-%d")
            transaction_info["transaction_id"] = str(transaction.id)
            transaction_info["transaction_type"] = transaction.transaction_type
            transaction_info["studentsdcid"] = str(transaction.transactee.student_dcid)
            transaction_data = {"tables": {"U_LUNCH_TRANSACTIONS": transaction_info}}
            powerschool_id = client.post_data(
                "ws/schema/table/U_LUNCH_TRANSACTIONS/", transaction_data
            )
            if powerschool_id:
                transaction.ps_transaction_id = powerschool_id
                transaction.save()
                count = count + 1

    return count
