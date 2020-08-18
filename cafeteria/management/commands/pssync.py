from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import timezone

import requests

from cafeteria.models import School
from lunchmanager.powerschool.powerschool import Powerschool
from profiles.models import Profile


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
        client = Powerschool()
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
        print('Synchronizing schools...')
        schools = client.schools()
        for item in schools:
            school, created = School.objects.update_or_create(id=item['id'], 
                defaults={
                    'name': item['name'],
                    'school_number': item['school_number']
                }
            )
        print('All schools successfully synchronized...')
            
    def sync_staff_using_client(self, client):
        print('Synchronizing staff...')
        active_staff = client.active_staff()
        newly_created = 0
        for member in active_staff:
            try:
                phone = 'x' + member['school_phone'][-4:]
            except:
                phone = 'x7900'
            try:
                room = member['homeroom']
            except:
                room = 'n/a'
            # look for an existing profile and create a new one if not found
            staff, created = Profile.objects.update_or_create(dcid=member['dcid'],
                defaults={
                    'last_sync': timezone.now(),
                    'lunch_id': member['lunch_id'],
                    'phone': phone,
                    'role': Profile.STAFF,
                    'room': room,
                    'status': True,
                    'user_number': member['teachernumber'],
                }
            )
            try:
                email_address = member['teacherloginid'] + '@nrcaknights.com'
            except:
                try:
                    email_address = member['loginid'] + '@nrcaknights.com'
                except:
                    email_address = member['dcid'] + '@nrcaknights.com'
            # if a new profile is created, create the corresponding user
            if created:
                user = User.objects.create(
                    first_name = member['first_name'],
                    last_name = member['last_name'],
                    email = email_address,
                    username = email_address,
                )
                staff.current_balance = 0
                staff.user = user
                staff.save()
                newly_created = newly_created + 1
            # if the staff member already exists, update the user info
            else:
                user = staff.user
                user.first_name = member['first_name']
                user.last_name = member['last_name']
                user.email = email_address
                user.username = email_address
                user.save()
            # if the staff member has a homeroom, update their roster
            homeroom_roster = client.homeroom_roster_for_teacher(staff.dcid)
            if homeroom_roster:
                try:
                    staff.grade_level = int(homeroom_roster[0]['grade_level'])
                except:
                    staff.grade_level = None
                staff.students.clear()
                for student in homeroom_roster:
                    try:
                        student = Profile.objects.get(dcid=int(student['dcid']))
                        staff.students.add(student)
                    except:
                        pass
                staff.save()
        print('Retreived {} staff, created {} new staff members'.format(len(active_staff), newly_created))

    def sync_students_using_client(self, client):
        print('Synchronizing students...')
        for school in School.objects.filter(active__exact=True):
            print('Sycning students from {} (id {})...'.format(school, school.id))
            active_students = client.studentsForSchool(school.id, 'lunch,school_enrollment')
            newly_created = 0
            for member in active_students:
                # look for an existing student and create a new one if not found
                student, created = Profile.objects.update_or_create(dcid=member['id'],
                    defaults={
                        'grade_level': member['school_enrollment']['grade_level'],
                        'last_sync': timezone.now(),
                        'lunch_id': member['lunch']['lunch_id'],
                        'role': Profile.STUDENT,
                        'school': School.objects.get(id=member['school_enrollment']['school_id']),
                        'status': True,
                        'user_number': member['local_id'],
                    }
                )
                try:
                    email_address = member['student_username'] + '@nrcaknights.com'
                except:
                    email_address = str(member['id']) + '@nrcaknights.com'
                # if a new student is created, create the corresponding user
                if created:
                    user = User.objects.create(
                        first_name = member['name']['first_name'],
                        last_name = member['name']['last_name'],
                        email = email_address,
                        username = email_address,
                    )
                    student.current_balance = 0
                    student.user = user
                    student.save()
                    newly_created = newly_created + 1
                # if the student already exists, update the user info
                else:
                    user = student.user
                    if user:
                        user.first_name = member['name']['first_name']
                        user.last_name = member['name']['last_name']
                        user.email = email_address
                        user.username = email_address
                        user.save()
                    else:
                        print('No user assigned to DCID: {}'.format(student.dcid))
                        user, created = User.objects.get_or_create(
                            first_name = member['name']['first_name'],
                            last_name = member['name']['last_name'],
                            email = email_address,
                            username = email_address,
                        )
                        student.user = user
                        student.save()
            print('Retreived {} students, created {} new students'.format(len(active_students), newly_created))



