import csv
import logging
import os

from django.core.management.base import BaseCommand

from cafeteria.models import SiteConfiguration
from profiles.models import Profile


logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = "Export student lunch balances for import into PowerSchool"

    def handle(self, *args, **options):
        logger.info("Exporting lunch balances...")
        file_path = SiteConfiguration.get_solo().balance_export_path
        students = Profile.objects.filter(active=True).filter(role=Profile.STUDENT)
        filename = os.path.join(file_path, "lunch_balance.csv")
        with open(filename, "w") as csvfile:
            csvwriter = csv.writer(csvfile)
            for student in students:
                csvwriter.writerow([student.user_number, student.current_balance])
        logger.info("Finished exporting lunch balances.")
