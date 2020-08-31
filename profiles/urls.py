from django.urls import include, path

from . import views

urlpatterns = [
    path('profile-autocomplete/', views.ProfileAutocomplete.as_view(), name='profile-autocomplete'),
    #path('<int:pk>/', views.DetailView.as_view(), name='detail'),
]