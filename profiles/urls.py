from django.urls import include, path

from profiles.views import ProfileDetailView, ProfileListView
from profiles.views import ProfileSearchResultsView

urlpatterns = [
    path('', ProfileListView.as_view(), name='profile-list'),
    path('<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('debtors/', ProfileListView.as_view(filter='debt'), name='profile-debt-list'),
    path('search/', ProfileSearchResultsView.as_view(), name='profile-search'),
]