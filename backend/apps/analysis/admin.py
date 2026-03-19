from django.contrib import admin
from .models import CropImage, AnalysisResult, Disease


@admin.register(CropImage)
class CropImageAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'crop_type', 'status', 'uploaded_at']
    list_filter   = ['status', 'crop_type']
    search_fields = ['user__email', 'original_filename']
    readonly_fields = ['id', 'uploaded_at', 'updated_at']


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display  = ['disease_name', 'confidence_score', 'is_healthy', 'severity', 'analyzed_at']
    list_filter   = ['is_healthy', 'severity']
    search_fields = ['disease_name', 'crop_image__user__email']
    readonly_fields = ['id', 'analyzed_at']


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display  = ['name', 'scientific_name', 'crop_type', 'severity_level']
    list_filter   = ['crop_type', 'severity_level']
    search_fields = ['name', 'scientific_name']
