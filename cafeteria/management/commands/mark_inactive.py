#
# mark_inactive.py
#
# Copyright (c) 2022 Doug Penny
# Licensed under MIT
#
# See LICENSE.md for license information
#
# SPDX-License-Identifier: MIT
#


from django.core.management.base import BaseCommand

from cafeteria.operations import check_for_inactive
from profiles.models import Profile


class Command(BaseCommand):
    help = "Check for students who are no longer active in PowerSchool and mark them as inactive."

    def add_arguments(self, parser):
        parser.add_argument(
            "-p",
            "--profile",
            type=int,
            help="Profile ID of the user you would like to process. If this is left blank, all users will be processed.",
        )

    def handle(self, *args, **options):
        if options["profile"]:
            profile = Profile.objects.filter(id=options["profile"]).exclude(
                role=Profile.GUARDIAN
            )
            check_for_inactive(profile)
        else:
            profiles = Profile.objects.filter(active=True).exclude(
                role=Profile.GUARDIAN
            )
            check_for_inactive(profiles)
