from datetime import timedelta
from typing import List
from django.db.models.query import QuerySet

from django.contrib.auth.models import User
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

def check_for_inactive(users: QuerySet):
    for user in users:
        # Check to see if the last sync was more than 2 days ago
        if user.last_sync.date() < timezone.now().date() + timedelta(days=-2):
            # Make sure the user's balance is zero before setting as inactive
            if user.current_balance != 0:
                user.pending = True
                user.save()
            else:
                user.active = False
                user.pending = False
                user.save()
                account = user.user
                account.active = False
                account.save()
