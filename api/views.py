#
# views.py
#
# Copyright (c) 2022 Doug Penny
# Licensed under MIT
#
# See LICENSE.md for license information
#
# SPDX-License-Identifier: MIT
#


from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

from rest_framework import filters
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api import serializers
from menu.models import MenuItem
from profiles.models import Profile
from transactions.models import Transaction


class UserSearch(generics.ListAPIView):
    search_fields = ['first_name', 'last_name']
    filter_backends = [filters.SearchFilter]
    queryset = User.objects.filter(is_active=True).filter(Q(profile__role=Profile.STUDENT) | Q(profile__role=Profile.STAFF))
    serializer_class = serializers.UserSearchSerializer


class ProfileSearch(generics.ListAPIView):
    search_fields = ['user__first_name', 'user__last_name']
    filter_backends = [filters.SearchFilter]
    queryset = Profile.objects.filter(active=True).exclude(pending=True).filter(Q(role=Profile.STUDENT) | Q(role=Profile.STAFF))
    serializer_class = serializers.ProfileSerializer


@api_view(['GET'])
def todays_menu_items(request):
    try:
        items = MenuItem.objects.filter(days_available__name=timezone.localdate(timezone.now()).strftime("%A")).filter(Q(category=MenuItem.ENTREE) | Q(app_only=True))
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = serializers.MenuItemSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def user_lookup(request, id):
    try:
        profile = Profile.objects.get(lunch_uuid=id)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = serializers.ProfileSerializer(profile)
    return Response(serializer.data)


@api_view(['GET'])
def user_order_lookup(request, id):
    try:
        profile = Profile.objects.get(lunch_uuid=id)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    try:
        order = Transaction.objects.filter(transactee=profile).filter(submitted__date=timezone.localdate(timezone.now())).filter(transaction_type=Transaction.DEBIT).filter(completed__isnull=True)
    except Transaction.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    profile = serializers.ProfileSerializer(profile).data
    order = serializers.OrderSerializer(order, many=True).data
    if len(order) == 0:
        order = [{ 'profile': profile }]
    elif len(order) == 1:
        order[0]['profile'] = profile
    else:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(order)


@api_view(['POST'])
def user_order_submit(request):
    print(request.data)
    serializer = serializers.OrderSubmissionSerializer(data=request.data)
    if serializer.is_valid():
        new_order = serializer.save()
        return Response({ 'order_id': new_order.id }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
