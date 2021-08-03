from django.contrib.auth.models import User
from rest_framework import serializers

from menu.models import MenuItem
from profiles.models import Profile


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'cost', 'days_available', 'lunch_period', 'name', 'sequence']


class UserSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()

    def get_text(self, obj):
        if obj.profile.role == Profile.STAFF:
            grade = 'Staff'
        else:
            grade = str(obj.profile.grade)
        return obj.first_name + ' ' + obj.last_name + ' - ' + grade

    class Meta:
        model = User
        fields = ['id', 'text']
