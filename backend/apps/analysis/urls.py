"""
===============================================================
🌱 KISHAN SATHI – Analysis URL Routing
Upload, Analyze, History, Analytics, Disease Library
===============================================================
"""

from django.urls import path
from .views import (
    CropImageUploadView, AnalyzeView,
    UploadAndAnalyzeView,
    HistoryListView, HistoryDetailView,
    AnalyticsView, DiseaseLibraryView,
)

app_name = 'analysis'

urlpatterns = [
    # ── Upload ────────────────────────────────────────────────
    path('upload/',          CropImageUploadView.as_view(),   name='upload'),
    path('upload-analyze/',  UploadAndAnalyzeView.as_view(),  name='upload-analyze'),

    # ── Analyze ───────────────────────────────────────────────
    path('analyze/<uuid:pk>/', AnalyzeView.as_view(),         name='analyze'),

    # ── History ───────────────────────────────────────────────
    path('history/',           HistoryListView.as_view(),     name='history-list'),
    path('history/<uuid:pk>/', HistoryDetailView.as_view(),   name='history-detail'),

    # ── Analytics ─────────────────────────────────────────────
    path('analytics/',         AnalyticsView.as_view(),       name='analytics'),

    # ── Disease Library ───────────────────────────────────────
    path('diseases/',          DiseaseLibraryView.as_view(),  name='disease-library'),
]
