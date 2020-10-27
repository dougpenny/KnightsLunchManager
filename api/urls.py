from django.urls import path

from api.views import DetailMenuItem
from api.views import ListMenuItem
from api.views import UserSearch

urlpatterns = [
    path('menu/', ListMenuItem.as_view()),
    path('menu/<int:pk>/', DetailMenuItem.as_view()),
    path('users/basic/', UserSearch.as_view(), name='basic-user-search'),
]
