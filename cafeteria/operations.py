from django.utils import timezone

from profiles.models import Profile
from transactions.models import Transaction


def end_of_year_process(year: str, profile: Profile = None):
    users = []
    if profile:
        users.append(profile)
    else:
        users = Profile.objects.all()
    for user in users:
        transactions = Transaction.objects.filter(transactee=user)
        if transactions.count() != 0:
            transactions.delete()
            temp_balance = user.current_balance
            user.current_balance = 0
            user.save()
            transaction = Transaction(
                amount=temp_balance,
                beginning_balance=user.current_balance,
                completed=timezone.now(),
                description='Ending balance from the {} school year.'.format(year),
                ending_balance=user.current_balance + temp_balance,
                submitted=timezone.now(),
                transactee=user,
                transaction_type=Transaction.CREDIT,
            )
            transaction.save()
            user.current_balance = transaction.ending_balance
            user.save()
