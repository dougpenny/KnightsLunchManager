import logging
from decimal import Decimal
from typing import List

from django.core.mail import EmailMessage, send_mail
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.template.loader import render_to_string
from django.utils import timezone

from constance import config

from profiles.models import Profile
from transactions.models import Transaction


logger = logging.getLogger(__file__)


class Command(BaseCommand):
	help = 'Audit current account balance based on transaction history.'

	def add_arguments(self, parser):
		group = parser.add_mutually_exclusive_group(required=True)
		group.add_argument(
			'-p',
			dest='profile_ids',
			type=int,
			help='One or more profile IDs to be audited.',
			nargs='+'
		)
		group.add_argument(
			'-a',
			'--all',
			action='store_true',
			help='Audit the current balance of all profiles.'
		)

	def handle(self, *args, **options):
		incorrect_balances = []
		if options['all']:
			all_users = Profile.objects.all()
			for user in all_users:
				audit_info = self.audit_current_balance(user.id)
				if audit_info:
					incorrect_balances.append(audit_info)
		else:
			for profile_id in options['profile_ids']:
				audit_info = self.audit_current_balance(profile_id)
				if audit_info:
					incorrect_balances.append(audit_info)
		if incorrect_balances:
				self.email_audit_report(incorrect_balances)

	def audit_current_balance(self, profile_id: int):
		user = Profile.objects.get(id=profile_id)
		transactions = Transaction.objects.filter(transactee=user)
		balance = 0
		for transaction in transactions:
			if transaction.transaction_type == Transaction.CREDIT:
				balance = balance + abs(transaction.amount)
			else:
				balance = balance - abs(transaction.amount)
		if user.current_balance != balance:
			logger.info("*** Incorrect Balance ***\n{}'s balance should be ${}, but is listed as ${}.".format(user.name(), balance, user.current_balance))
			return [user.name, transactions.count(), user.current_balance, balance]
		else:
			return None

	def email_audit_report(self, incorrect_balances: List):
		recipients_list = config.REPORTS_EMAIL.split(',')
		context = {
			'time': timezone.now(),
			'items': incorrect_balances
		}
		html_message = render_to_string('email/balance_audit_report.html', context=context)
		msg = EmailMessage('Lunch Balance Audit Report', html_message, None, recipients_list)
		msg.content_subtype = 'html'
		msg.send()


