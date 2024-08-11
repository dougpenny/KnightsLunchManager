#
# balancecorrection.py
#
# Copyright (c) 2022 Doug Penny
# Licensed under MIT
#
# See LICENSE.md for license information
#
# SPDX-License-Identifier: MIT
#


import logging
from decimal import Decimal

from django.core.management.base import BaseCommand

from profiles.models import Profile
from transactions.models import Transaction


logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = "Correct current lunch balance by reprocessing each transaction."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "-p",
            dest="profile_ids",
            type=int,
            help="One or more profile IDs to be corrected.",
            nargs="+",
        )
        group.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="Correct the current balance of all profiles. (This may take a long time!)",
        )

    def handle(self, *args, **options):
        if options["all"]:
            all_users = Profile.objects.filter(active=True)
            for user in all_users:
                self.correct_current_balance(user)
        else:
            for profile_id in options["profile_ids"]:
                self.correct_current_balance(Profile.objects.get(id=profile_id))

    def correct_current_balance(self, profile: Profile):
        transactions = Transaction.objects.filter(transactee=profile).order_by(
            "completed", "submitted"
        )
        if transactions.count() > 0:
            balance = Decimal(0)
            for transaction in transactions:
                transaction.beginning_balance = balance
                if transaction.transaction_type == Transaction.CREDIT:
                    balance = balance + transaction.amount
                else:
                    balance = balance - abs(transaction.amount)
                transaction.ending_balance = balance
                transaction.save()
            profile.current_balance = balance
            profile.save()
            logger.info(
                "\n*** Balance Corrected for {} ***\n{} transactions were reprocessed".format(
                    profile.name(), transactions.count()
                )
            )
