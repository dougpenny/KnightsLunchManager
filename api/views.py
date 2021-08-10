from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

from rest_framework import filters
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response

from api import serializers
from menu.models import MenuItem
from profiles.models import Profile
from transactions.models import Transaction


class TodaysMenuItems(generics.ListAPIView):
    queryset = MenuItem.objects.filter(days_available__name=timezone.localdate(timezone.now()).strftime("%A")).filter(
        Q(category=MenuItem.ENTREE) | Q(app_only=True))
    serializer_class = serializers.MenuItemSerializer


class DetailMenuItem(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = serializers.MenuItemSerializer


class TodaysOrders(generics.ListAPIView):
    queryset = Transaction.objects.filter(submitted__date=timezone.localdate(timezone.now()))
    serializer_class = serializers.OrderSerializer


class UserSearch(generics.ListCreateAPIView):
    search_fields = ['first_name', 'last_name']
    filter_backends = [filters.SearchFilter]
    queryset = User.objects.filter(is_active=True).filter(
        Q(profile__role=Profile.STUDENT) | Q(profile__role=Profile.STAFF))
    serializer_class = serializers.UserSearchSerializer


@api_view(['GET', 'POST', 'DELETE'])
def user_order_lookup(request, id):
    try:
        order = Transaction.objects.filter(transactee__lunch_uuid=id).filter(submitted__date=timezone.localdate(timezone.now()))
    except Transaction.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = serializers.OrderSerializer(order, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = serializers.OrderSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)