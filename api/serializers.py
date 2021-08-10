from django.contrib.auth.models import User
from rest_framework import serializers

from menu.models import MenuItem
from profiles.models import Profile
from transactions.models import MenuLineItem, Transaction


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'cost', 'days_available', 'name', 'sequence', 'short_name']


class MenuLineItemSerializer(serializers.ModelSerializer):
    menu_item = MenuItemSerializer()

    class Meta:
        model = MenuLineItem
        fields = ['menu_item', 'quantity']

    def create(self, validated_data):
        print('create line item: {}'.format(**validated_data))
        menu_item_data = validated_data.pop('menu_item')
        line_item = MenuLineItem.objects.create(**validated_data)
        for menu_item in menu_item_data:
            print(**menu_item)
        return line_item

    def update(self, instance, validated_data):
        print('update line item: {}'.format(**validated_data))
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    grade = serializers.StringRelatedField()

    class Meta:
        model = Profile
        fields = ['current_balance', 'grade', 'lunch_uuid', 'name']


class OrderSerializer(serializers.ModelSerializer):
    line_item = MenuLineItemSerializer(many=True)
    transactee = ProfileSerializer()
    
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'description', 'submitted', 'transactee', 'line_item']
    
    def create(self, validated_data):
        print('create order: {}'.format(**validated_data))
        line_item_data = validated_data.pop('line_item')
        order = Transaction.objects.create(**validated_data)
        for line_item in line_item_data:
            MenuLineItem.objects.create(transaction=order, **line_item)
        return order
    
    def update(self, instance, validated_data):
        print('update order: {}'.format(**validated_data))
        return instance

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
