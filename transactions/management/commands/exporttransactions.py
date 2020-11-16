from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

import logging
import requests

from profiles.models import Profile
from transactions.models import Transaction
from transactions import utils


logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Exports completed transactions from Lunch Manager to PowerSchool. By default, all completed transactions are exported. However, you can also choose: day - past 24 hours, week - past 7 days, or month - past 30 days.'

    def add_arguments(self, parser):
        parser.add_argument(
            'range',
            choices=['all', 'day', 'week', 'month'],
            default='all',
            help='Select the date range of transactions to export to PowerSchool. The default is to export ALL transactions.',
            nargs='?'
        )

    def handle(self, *args, **options):
        transactions = Transaction.objects.filter(
            completed__isnull=False,
            ps_transaction_id__isnull=True,
            transactee__role=Profile.STUDENT
        )
        today = timezone.now()
        if options['range'] == 'day':
            yesterday = timedelta(days=-1)
            transactions = transactions.filter(completed__date__gte=today + yesterday)
        elif options['range'] == 'week':
            past_week = timedelta(days=-7)
            transactions = transactions.filter(completed__date__gte=today + past_week)
        elif options['range'] == 'month':
            past_month = timedelta(days=-30)
            transactions = transactions.filter(completed__date__gte=today + past_month)
        logger.info('Exporting {} transactions to PowerSchool...'.format(transactions.count()))
        count = utils.export_transactions(transactions)
        logger.info('Completed exporting {} transactions to PowerSchool.'.format(count))
