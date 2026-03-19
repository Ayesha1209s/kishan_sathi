"""
===============================================================
🌱 KISHAN SATHI – Analysis Serializers
CropImage upload, AnalysisResult, History
===============================================================
"""

import os
from django.conf import settings
from rest_framework import serializers
from .models import CropImage, AnalysisResult, Disease


# ──────────────────────────────────────────────────────────────
# 📷 CROP IMAGE UPLOAD SERIALIZER
# ──────────────────────────────────────────────────────────────
class CropImageUploadSerializer(serializers.ModelSerializer):
    """Validates and saves uploaded crop image."""

    class Meta:
        model  = CropImage
        fields = ['id', 'image', 'crop_type', 'notes', 'original_filename',
                  'file_size', 'status', 'uploaded_at']
        read_only_fields = ['id', 'original_filename', 'file_size', 'status', 'uploaded_at']

    def validate_image(self, value):
        # Validate content type
        allowed_types = getattr(settings, 'ALLOWED_IMAGE_TYPES',
                                ['image/jpeg', 'image/png', 'image/webp'])
        if hasattr(value, 'content_type') and value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"Unsupported file type '{value.content_type}'. Allowed: JPG, PNG, WEBP."
            )

        # Validate file size
        max_mb = getattr(settings, 'MAX_IMAGE_SIZE_MB', 10)
        if value.size > max_mb * 1024 * 1024:
            raise serializers.ValidationError(
                f"File too large ({value.size / 1024 / 1024:.1f} MB). Maximum allowed: {max_mb} MB."
            )

        # Validate extension
        ext = os.path.splitext(value.name)[1].lower()
        allowed_exts = getattr(settings, 'ALLOWED_IMAGE_EXTENSIONS', ['.jpg', '.jpeg', '.png', '.webp'])
        if ext not in allowed_exts:
            raise serializers.ValidationError(
                f"Invalid extension '{ext}'. Allowed: {', '.join(allowed_exts)}."
            )

        return value

    def create(self, validated_data):
        image = validated_data.get('image')
        if image:
            validated_data['original_filename'] = image.name
            validated_data['file_size']         = image.size
        return super().create(validated_data)


# ──────────────────────────────────────────────────────────────
# 📊 ANALYSIS RESULT SERIALIZER
# ──────────────────────────────────────────────────────────────
class AnalysisResultSerializer(serializers.ModelSerializer):
    processed_image_url = serializers.ReadOnlyField()

    class Meta:
        model  = AnalysisResult
        fields = [
            'id', 'disease_name', 'scientific_name', 'is_healthy',
            'confidence_score', 'severity',
            'description', 'symptoms', 'cause',
            'chemical_treatment', 'organic_treatment', 'preventive_measures',
            'processed_image', 'processed_image_url', 'bounding_box',
            'alternative_predictions', 'model_version',
            'processing_time', 'analyzed_at',
        ]
        read_only_fields = fields


# ──────────────────────────────────────────────────────────────
# 📋 CROP IMAGE LIST (brief, for history)
# ──────────────────────────────────────────────────────────────
class CropImageListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for history lists."""
    image_url    = serializers.ReadOnlyField()
    disease_name = serializers.SerializerMethodField()
    confidence   = serializers.SerializerMethodField()
    is_healthy   = serializers.SerializerMethodField()

    class Meta:
        model  = CropImage
        fields = ['id', 'image_url', 'crop_type', 'original_filename',
                  'status', 'disease_name', 'confidence', 'is_healthy',
                  'uploaded_at']

    def get_disease_name(self, obj):
        return obj.result.disease_name if obj.has_result else None

    def get_confidence(self, obj):
        return obj.result.confidence_score if obj.has_result else None

    def get_is_healthy(self, obj):
        return obj.result.is_healthy if obj.has_result else None


# ──────────────────────────────────────────────────────────────
# 🔍 CROP IMAGE DETAIL (full, for result page)
# ──────────────────────────────────────────────────────────────
class CropImageDetailSerializer(serializers.ModelSerializer):
    """Full serializer including nested result."""
    image_url = serializers.ReadOnlyField()
    result    = AnalysisResultSerializer(read_only=True)

    class Meta:
        model  = CropImage
        fields = ['id', 'image_url', 'crop_type', 'original_filename',
                  'file_size', 'notes', 'status', 'result',
                  'uploaded_at', 'updated_at']


# ──────────────────────────────────────────────────────────────
# 📈 ANALYTICS SERIALIZER
# ──────────────────────────────────────────────────────────────
class AnalyticsSerializer(serializers.Serializer):
    """Dashboard analytics summary data."""
    period            = serializers.CharField()
    total_uploads     = serializers.IntegerField()
    diseases_found    = serializers.IntegerField()
    healthy_crops     = serializers.IntegerField()
    avg_confidence    = serializers.FloatField()
    daily_data        = serializers.ListField()
    top_diseases      = serializers.ListField()


# ──────────────────────────────────────────────────────────────
# 🦠 DISEASE LIBRARY SERIALIZER
# ──────────────────────────────────────────────────────────────
class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Disease
        fields = '__all__'
