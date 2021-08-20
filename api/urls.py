from django.urls import path

from api import views

urlpatterns = [
    path('menu/entrees/today', views.todays_menu_items, name='todays-items'),
    path('order/<uuid:id>', views.user_order_lookup, name='user-order'),
    path('order/submit', views.user_order_submit, name='submit-order'),
    path('user/<uuid:id>', views.user_lookup, name='user-lookup'),
    path('users/basic/', views.UserSearch.as_view(), name='basic-user-search'),
    path('profile/basic/', views.ProfileSearch.as_view(), name='basic-profile-search'),
]
