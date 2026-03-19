"""
===============================================================
🌱 KISHAN SATHI – Accounts URL Routing
Auth, Profile, Password management endpoints
===============================================================
"""

from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView,
    ProfileView, ProfileImageUploadView,
    ChangePasswordView, UserActivityView,
    UserDashboardView,
)

app_name = 'accounts'

urlpatterns = [
    # ── Authentication ────────────────────────────────────────
    path('register/',        RegisterView.as_view(),        name='register'),
    path('login/',           LoginView.as_view(),           name='login'),
    path('logout/',          LogoutView.as_view(),          name='logout'),

    # ── Profile ───────────────────────────────────────────────
    path('profile/',         ProfileView.as_view(),         name='profile'),
    path('profile/image/',   ProfileImageUploadView.as_view(), name='profile-image'),

    # ── Password ──────────────────────────────────────────────
    path('change-password/', ChangePasswordView.as_view(),  name='change-password'),

    # ── Activity & Dashboard ──────────────────────────────────
    path('activity/',        UserActivityView.as_view(),    name='activity'),
    path('dashboard/',       UserDashboardView.as_view(),   name='dashboard'),
]
