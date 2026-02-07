#
# config/urls.py
#
# Copyright (c) 2026 Doug Penny
# Licensed under MIT
#
# See LICENSE.md for license information
#
# SPDX-License-Identifier: MIT
#

from django.contrib import admin
from django.urls import include, path


admin.site.site_header = "NRCA Cafeteria"
admin.site.site_title = "NRCA Cafeteria"
admin.site.index_title = "Welcome to the NRCA Cafeteria Portal"

urlpatterns = [
    path("", include("cafeteria.urls")),
    path("backally/", admin.site.urls, name="django-admin"),
    path("api/v1/", include("api.urls")),
    path("oauth2/", include("django_auth_adfs.urls")),
]
