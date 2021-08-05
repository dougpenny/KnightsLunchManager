import uuid

from django.contrib.auth.models import User
from django.db import models

from cafeteria.models import GradeLevel, School


class Profile(models.Model):
    GUARDIAN = 3
    STAFF = 1
    STUDENT = 2
    ROLE_CHOICES = [
        (GUARDIAN, 'Guardian'),
        (STAFF, 'Staff'),
        (STUDENT, 'Student'),
    ]
    current_balance = models.DecimalField(
        default=0, decimal_places=2, max_digits=6)
    grade = models.ForeignKey(GradeLevel, on_delete=models.CASCADE, default=None, null=True)
    children = models.ManyToManyField(
        'self',
        blank=True,
        related_name='guardians',
        related_query_name='guardian',
        symmetrical=False
    )
    homeroom_teacher = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        related_name='students',
        related_query_name='student',
        verbose_name='Homeroom Teacher'
    )
    last_sync = models.DateTimeField()
    lunch_id = models.IntegerField(default=None, null=True, verbose_name='Lunch ID')
    lunch_uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone = models.CharField(max_length=5, blank=True, default='')
    role = models.SmallIntegerField(choices=ROLE_CHOICES, default=STUDENT)
    room = models.TextField(max_length=64, blank=True, default='')
    school = models.ForeignKey(School, null=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=False)
    pending = models.BooleanField(default=False)
    student_dcid = models.IntegerField(blank=True, null=True, unique=True, verbose_name='Student DCID')
    user_dcid = models.IntegerField(blank=True, null=True, unique=True, verbose_name='User DCID')
    user_number = models.IntegerField(blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return self.name()

    def last_first(self):
        return self.user.last_name + ', ' + self.user.first_name
    last_first.admin_order_field = 'user__last_name'

    def name(self):
        return self.user.first_name + ' ' + self.user.last_name
    name.admin_order_field = 'user__last_name'
