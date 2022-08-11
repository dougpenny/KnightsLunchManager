import uuid

from profiles.models import Profile
from transactions.helpers import process_transaction
from transactions.models import Transaction


def process_inactive(profile: Profile) -> Profile:
    balance = profile.current_balance

    # Zero out the balance
    description = "Balance transferred to the Business Office"
    transaction_type = Transaction.DEBIT
    if balance < 0:
        description = "Balance settled by the Business Office"
        transaction_type = Transaction.CREDIT
    transaction = Transaction(
        amount=abs(balance),
        description=description,
        transaction_type=transaction_type,
        transactee=profile
    )
    transaction.save()
    process_transaction(transaction)

    # Reset lunch card ID and make user inactive
    profile.lunch_uuid = uuid.uuid4()
    profile.cards_printed = 0
    profile.active = False
    profile.pending = False
    profile.save()
    profile.user.is_active = False
    profile.user.save()

    return profile
