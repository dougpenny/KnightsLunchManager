from django.urls import include, path

from cafeteria import views

urlpatterns = [
    path('', views.index, name='index'),
    path('delete-order/', views.delete_order, name='delete'),
    path('submit-order/', views.submit_order, name='submit'),
    path('todays-order/', views.todays_order, name='today'),
    
    path('admin/', views.admin_dashboard, name='admin'),
    path('admin/homeroom-orders-report', views.homeroom_orders_report, name='homerooms-report'),
    path('admin/transactions/', include('transactions.urls')),
    path('admin/profiles/', include('profiles.urls')),
]