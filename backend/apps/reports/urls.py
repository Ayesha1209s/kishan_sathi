from django.urls import path
from .views import (
    GenerateSingleReportView, GenerateSummaryReportView,
    DownloadReportView, ReportListView,
)

app_name = 'reports'

urlpatterns = [
    path('',                            ReportListView.as_view(),           name='list'),
    path('generate/<uuid:pk>/',         GenerateSingleReportView.as_view(), name='generate-single'),
    path('generate-summary/',           GenerateSummaryReportView.as_view(),name='generate-summary'),
    path('download/<uuid:pk>/',         DownloadReportView.as_view(),       name='download'),
]
