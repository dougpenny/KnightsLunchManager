from django.contrib.auth.models import User
from rest_framework import serializers

from menu.models import MenuItem


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'cost', 'days_available', 'schools_available', 'name', 'sequence']


class UserSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.first_name + ' ' + obj.last_name + ' - ' + str(obj.profile.grade_level)

    class Meta:
        model = User
        fields = ['id', 'name']