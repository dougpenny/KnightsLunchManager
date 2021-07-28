import logging

from datetime import timedelta
from typing import List
from django.db.models.query import QuerySet

from django.contrib.auth.models import User
from django.utils import timezone

from profiles.models import Profile
from transactions.models import Transaction


logger = logging.getLogger(__file__)


def end_of_year_process(year: str, profile: Profile = None):
    users = []
    if profile:
        users.append(profile)
    else:
        users = Profile.objects.filter(active=True)
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

def check_for_inactive(profiles: QuerySet):
    for profile in profiles:
        # Check to see if the last sync was more than 2 days ago
        if profile.last_sync.date() < timezone.now().date() + timedelta(days=-2):
            # Make sure the user's balance is zero before setting as inactive
            if profile.current_balance != 0:
                profile.pending = True
                profile.save()
                logger.info('{} has a current balance of {}; marked pending inactive.'.format(profile.name(), profile.current_balance))
            else:
                profile.active = False
                profile.pending = False
                profile.save()
                account = profile.user
                account.is_active = False
                account.save()
                logger.info('{} has not synced from PowerSchool in more than 2 days; marked inactive.'.format(profile.name()))
