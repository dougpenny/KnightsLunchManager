from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import filters
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response

from api.serializers import MenuItemSerializer
from api.serializers import UserSerializer
from menu.models import MenuItem
from profiles.models import Profile


class ListMenuItem(generics.ListCreateAPIView):
    search_fields = ['name']
    filter_backends = [filters.SearchFilter]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class DetailMenuItem(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


class UserSearch(generics.ListCreateAPIView):
    search_fields = ['first_name', 'last_name']
    filter_backends = [filters.SearchFilter]
    queryset = User.objects.filter(is_active=True).filter(
        Q(profile__role=Profile.STUDENT) | Q(profile__role=Profile.STAFF))
    serializer_class = UserSerializer
