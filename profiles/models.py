from django.contrib.auth.models import User
from django.db import models

from cafeteria.models import School


class Profile(models.Model):
    STAFF = 1
    STUDENT = 2
    ROLE_CHOICES = [
        (STAFF, 'Staff'),
        (STUDENT, 'Student'),
    ]
    current_balance = models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)
    grade_level = models.SmallIntegerField(default=None, null=True)
    homeroom_teacher = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        related_name='students',
        related_query_name='student'
    )
    last_sync = models.DateTimeField()
    lunch_id = models.IntegerField(default=None, null=True)
    phone = models.CharField(max_length=5, blank=True, default='')
    role = models.SmallIntegerField(choices=ROLE_CHOICES, default=STUDENT)
    room = models.TextField(max_length=64, blank=True, default='')
    school = models.ForeignKey(School, null=True, on_delete=models.SET_NULL)
    status = models.BooleanField(default=False)
    student_dcid = models.IntegerField(blank=True, null=True, unique=True)
    user_dcid = models.IntegerField(blank=True, null=True, unique=True)
    user_number = models.IntegerField(blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name()

    def last_first(self):
        return self.user.last_name + ', ' + self.user.first_name
    last_first.admin_order_field = 'user__last_name'

    def name(self):
        return self.user.first_name + ' ' + self.user.last_name
    name.admin_order_field = 'user__last_name'