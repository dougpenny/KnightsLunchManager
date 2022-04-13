#
# process_eoy.py
#
# Copyright (c) 2022 Doug Penny
# Licensed under MIT
#
# See LICENSE.md for license information
#
# SPDX-License-Identifier: MIT
#


from django.core.management.base import BaseCommand

from constance import config

from cafeteria.operations import end_of_year_process
from profiles.models import Profile


class Command(BaseCommand):
    help = 'Complete the end of year process in preparation for the next school year.'

    def add_arguments(self, parser):
        parser.add_argument(
            '-p',
            '--profile',
            type=int,
            help='Profile ID of the user you would like to process. If this is left blank, all users will be processed.',
        )
        parser.add_argument(
            '-y',
            '--year',
            default=config.CURRENT_YEAR,
            type=str,
            help='Override the currently set school year; used when creating the rollover balance transaction. For example, entering 2019-2020 here would result in a transaction description of "Ending balance from the 2019-2020 school year."',
        )

    def handle(self, *args, **options):
        if options['profile']:
            profile = Profile.objects.get(id=options['profile'])
            end_of_year_process(options['year'], profile)
        else:
            end_of_year_process(options['year'])