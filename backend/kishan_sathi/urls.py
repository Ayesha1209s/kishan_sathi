"""
===============================================================
🌱 KISHAN SATHI – Root URL Configuration
===============================================================
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # ── Django Admin ──────────────────────────────────────────
    path('admin/', admin.site.urls),

    # ── API v1 ────────────────────────────────────────────────
    path('api/v1/auth/',          include('apps.accounts.urls')),
    path('api/v1/analysis/',      include('apps.analysis.urls')),
    path('api/v1/reports/',       include('apps.reports.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),

    # ── JWT Token Refresh ─────────────────────────────────────
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# ── Serve media files in development ──────────────────────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
