#
# sync_powerschool.py
#
# Copyright (c) 2022 Doug Penny
# Licensed under MIT
#
# See LICENSE.md for license information
#
# SPDX-License-Identifier: MIT
#


import logging

from django.core.management.base import BaseCommand

from cafeteria import pssync


logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Synchronize resources from PowerSchool to Lunch Manager'

    def add_arguments(self, parser):
        parser.add_argument(
            'resource',
            choices=['all', 'schools', 'staff', 'students'],
            default='all',
            help='Select the resource to sycn from PowerSchool. The default is to sync ALL resources.',
            nargs='?'
        )

    def handle(self, *args, **options):
        client = pssync.new_powerschool_client()

        if options['resource'] == 'all':
            pssync.sync_powerschool(client)
        elif options['resource'] == 'schools':
            pssync.sync_powerschool_schools(client)
        elif options['resource'] == 'staff':
            pssync.sync_powerschool_staff(client)
        elif options['resource'] == 'students':
            pssync.sync_powerschool_students(client)
