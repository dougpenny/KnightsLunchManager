from django.urls import path

from api.views import DetailMenuItem
from api.views import ListMenuItem
from api.views import StudentSearch

urlpatterns = [
    path('menu/', ListMenuItem.as_view()),
    path('menu/<int:pk>/', DetailMenuItem.as_view()),
    path('students/basic/', StudentSearch.as_view(), name='basic-student-search'),
]