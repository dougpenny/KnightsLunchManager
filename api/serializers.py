#
# serializers.py
#
# Copyright (c) 2022 Doug Penny
# Licensed under MIT
#
# See LICENSE.md for license information
#
# SPDX-License-Identifier: MIT
#


from django.contrib.auth.models import User
from rest_framework import serializers

from menu.models import MenuItem
from profiles.models import Profile
from transactions import helpers
from transactions.models import MenuLineItem, Transaction


class ExistingOrderMenuItemSerializer(serializers.ModelSerializer):
    cost = serializers.DecimalField(max_digits=None, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = MenuItem
        fields = ['cost', 'id', 'name']


class MenuItemSerializer(serializers.ModelSerializer):
    cost = serializers.DecimalField(max_digits=None, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = MenuItem
        fields = ['app_only', 'category', 'cost', 'id', 'name', 'sequence', 'short_name']


class MenuLineItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer()

    class Meta:
        model = MenuLineItem
        fields = ['menu_item', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    line_item = MenuLineItemSerializer(many=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'line_item']


class OrderSubmissionSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.IntegerField())
    temp_trans = serializers.IntegerField(required=False)
    transactee = serializers.IntegerField()

    def create(self, validated_data):
        order = helpers.create_order(validated_data)
        if order:
            helpers.process_transaction(order)
        return order


class ProfileSerializer(serializers.ModelSerializer):
    grade = serializers.SerializerMethodField()

    def get_grade(self, obj):
        if obj.role != Profile.STUDENT:
            return "Staff"
        return str(obj.grade)

    class Meta:
        model = Profile
        fields = ['current_balance', 'grade', 'id', 'lunch_uuid', 'name', 'user_number']


class UserSearchSerializer(serializers.ModelSerializer):
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
