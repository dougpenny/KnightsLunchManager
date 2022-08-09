#
# pssync.py
#
# Copyright (c) 2022 Doug Penny
# Licensed under MIT
#
# See LICENSE.md for license information
#
# SPDX-License-Identifier: MIT
#


from asgiref.sync import async_to_sync
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.utils import timezone

import logging
import os

from pypowerschool import powerschool

from cafeteria.models import GradeLevel, School
from profiles.models import Profile


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
        base_url = os.getenv('POWERSCHOOL_URL')
        client_id = os.getenv('POWERSCHOOL_CLIENT_ID')
        client_secret = os.getenv('POWERSCHOOL_CLIENT_SECRET')
        client = powerschool.Client(base_url, client_id, client_secret)

        if options['resource'] == 'all':
            self.sync_schools_using_client(client)
            self.sync_students_using_client(client)
            self.sync_staff_using_client(client)
        elif options['resource'] == 'schools':
            self.sync_schools_using_client(client)
        elif options['resource'] == 'staff':
            self.sync_staff_using_client(client)
        elif options['resource'] == 'students':
            self.sync_students_using_client(client)

    def sync_schools_using_client(self, client):
        logger.info('Synchronizing schools...')
        schools = async_to_sync(client.schools_in_district)()
        for item in schools:
            school, created = School.objects.update_or_create(id=item['id'], defaults={
                'name': item['name'],
                'school_number': item['school_number']
            })
            if (created is False and school.active is True):
                start = item['low_grade']
                end = item['high_grade']
                for grade_level in range(start, end + 1):
                    grade, created = GradeLevel.objects.update_or_create(value=grade_level, defaults={
                        'school': school
                    })
        logger.info('All schools successfully synchronized...')

    def sync_staff_using_client(self, client):
        logger.info('Synchronizing staff...')
        active_staff = client.powerquery("ws/schema/query/com.nrcaknights.knightslunch.teachers.active_staff")
        newly_created = 0
        for member in active_staff:
            email_address = member.get('email')
            # if the staff member does not have an email address, they are skipped
            if email_address:
                school_phone = member.get('school_phone')
                if school_phone:
                    phone = f'x{school_phone[-4:]}'
                else:
                    phone = 'x7900'
                room = member.get('homeroom', 'n/a')

                # look for an existing profile and create a new one if not found
                staff, created = Profile.objects.update_or_create(user_dcid=member['dcid'], defaults={
                    'last_sync': timezone.now(),
                    'phone': phone,
                    'role': Profile.STAFF,
                    'room': room,
                    'active': True,
                    'user_number': member['teacher_number'],
                })

                # if a new profile is created, create the corresponding user
                if created:
                    user, created = User.objects.get_or_create(
                        first_name=member['first_name'],
                        last_name=member['last_name'],
                        email=email_address,
                        username=email_address,
                    )
                    staff.user = user
                    staff.save()
                    newly_created = newly_created + 1
                # if the staff member already exists, update the user info
                else:
                    user = staff.user
                    if user:
                        user.first_name = member['first_name']
                        user.last_name = member['last_name']
                        user.email = email_address
                        user.username = email_address
                        user.is_active = True
                        user.save()
                    else:
                        user, created = User.objects.get_or_create(
                            first_name=member['first_name'],
                            last_name=member['last_name'],
                            email=email_address,
                            username=email_address,
                        )
                        staff.user = user
                        staff.save()

                # if the staff member has a homeroom, update their roster
                homeroom_roster = client.powerquery("ws/schema/query/com.nrcaknights.knightslunch.students.homeroom_roster", {'teacher_dcid': staff.user_dcid})
                if homeroom_roster:
                    try:
                        grade_level = homeroom_roster[0]['grade_level']
                        count = 1
                        while grade_level == "" and count < len(homeroom_roster):
                            grade_level = homeroom_roster[count]['grade_level']
                            count = count + 1
                        staff.grade = GradeLevel.objects.get(value=int(grade_level))
                    except Exception:
                        staff.grade = None
                        logger.error('No grade level assigned to homeroom teacher: {}'.format(staff.name()))
                    staff.students.clear()
                    for student in homeroom_roster:
                        try:
                            student = Profile.objects.get(student_dcid=int(student['dcid']))
                            staff.students.add(student)
                        except Exception:
                            pass
                else:
                    staff.grade = None
                staff.save()
        logger.info('Retrieved {} staff, created {} new staff members'.format(len(active_staff), newly_created))

    def sync_students_using_client(self, client):
        logger.info('Synchronizing students...')
        for school in School.objects.filter(active=True):
            logger.info('Sycning students from {} (id {})...'.format(school, school.id))
            active_students = client.powerquery("ws/schema/query/com.nrcaknights.knightslunch.students.student_info", {'school_dcid': school.id})
            newly_created = 0
            for member in active_students:
                email_address = member.get('email')
                if not email_address:
                    student_number = member.get('student_number')
                    email_address = f'{student_number}@nrcaknigihts.com'

                # if the student does not have an email address, they are skipped
                if email_address:
                    # look for an existing student and create a new one if not found
                    grade = GradeLevel.objects.get(value=int(member['grade_level']))
                    student, created = Profile.objects.update_or_create(student_dcid=member['student_dcid'], defaults={
                        'grade': grade,
                        'last_sync': timezone.now(),
                        'role': Profile.STUDENT,
                        'school': School.objects.get(id=int(member['school_dcid'])),
                        'active': True,
                        'user_number': member['student_number'],
                    })
      
                    # if a new student is created, create the corresponding user
                    if created:
                        user, created = User.objects.get_or_create(
                            first_name=member['first_name'],
                            last_name=member['last_name'],
                            email=email_address,
                            username=email_address,
                        )
                        student.user = user
                        student.save()
                        newly_created = newly_created + 1
                    # if the student already exists, update the user info
                    else:
                        user = student.user
                        if user:
                            user.first_name = member['first_name']
                            user.last_name = member['last_name']
                            user.email = email_address
                            user.username = email_address
                            user.is_active = True
                            user.save()
                        else:
                            user, created = User.objects.get_or_create(
                                first_name=member['first_name'],
                                last_name=member['last_name'],
                                email=email_address,
                                username=email_address,
                            )
                            student.user = user
                            student.save()
            logger.info('Retreived {} students, created {} new students'.format(len(active_students), newly_created))
