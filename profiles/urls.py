from django.urls import include, path

from profiles.views import ProfileDetailView, ProfileListView, ProfileSearchResultsView

urlpatterns = [
    path('', ProfileListView.as_view(), name='profile-list'),
    path('<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('search/', ProfileSearchResultsView.as_view(), name='profile-search'),
]