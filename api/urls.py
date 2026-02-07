#
# urls.py
#
# Copyright (c) 2026 Doug Penny
# Licensed under MIT
#
# See LICENSE.md for license information
#
# SPDX-License-Identifier: MIT
#


from django.urls import path

from api import views

urlpatterns = [
    path("auth/session", views.session_key, name="create-session"),
    path("menu/entrees/today", views.todays_menu_items, name="todays-items"),
    path("order/<uuid:id>", views.user_order_lookup, name="user-order"),
    path("order/submit", views.user_order_submit, name="submit-order"),
    path("user/<uuid:id>", views.user_lookup, name="user-lookup"),
    path("users/basic/", views.UserSearch.as_view(), name="basic-user-search"),
    path("profile/basic/", views.ProfileSearch.as_view(), name="basic-profile-search"),
    path("profile/lunchid/", views.LunchIdSearch.as_view(), name="lunch-id-search"),
]
