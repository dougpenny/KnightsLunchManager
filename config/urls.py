"""lunchmanager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path


admin.site.site_header = "NRCA Cafeteria"
admin.site.site_title = "NRCA Cafeteria"
admin.site.index_title = "Welcome to the NRCA Cafeteria Portal"

urlpatterns = [
    path('', include('cafeteria.urls')),
    path('backally/', admin.site.urls, name='django-admin'),
    path('api/v1/', include('api.urls')),
    path('oauth2/', include('django_auth_adfs.urls')),
]
