from django.core.management.base import BaseCommand

import csv
import logging
import os

from profiles.models import Profile


logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Export student lunch balances for import into PowerSchool'

    def handle(self, *args, **options):
        logger.info('Exporting lunch balances...')
        file_path = os.getenv('BALANCE_EXPORT_PATH')
        students = Profile.objects.filter(role=Profile.STUDENT)
        fields = ['student_number', 'balance1']
        filename = os.path.join(file_path, 'lunch_balance.csv')
        with open(filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(fields)
            for student in students:
                csvwriter.writerow([student.user_number, student.current_balance])
        logger.info('Finished exporting lunch balances.')
