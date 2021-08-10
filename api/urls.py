from django.urls import path

from api import views

urlpatterns = [
    path('menu/entrees/today', views.TodaysMenuItems.as_view()),
    path('menu/<int:pk>', views.DetailMenuItem.as_view()),
    path('order/<uuid:id>', views.user_order_lookup, name='user-order'),
    path('orders/today', views.TodaysOrders.as_view(), name='todays-orders'),
    path('users/basic/', views.UserSearch.as_view(), name='basic-user-search'),
]
