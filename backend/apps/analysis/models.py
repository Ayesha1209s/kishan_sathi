"""
===============================================================
🌱 KISHAN SATHI – Analysis Models
CropImage + AnalysisResult + AI Disease data
===============================================================
"""

import os
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


def crop_image_path(instance, filename):
    """Upload path: media/uploads/<user_id>/<uuid>.<ext>"""
    ext  = filename.split('.')[-1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('uploads', str(instance.user.id), name)


def processed_image_path(instance, filename):
    """Upload path for heatmap/bounding box overlay images."""
    ext  = filename.split('.')[-1].lower()
    name = f"processed_{uuid.uuid4().hex}.{ext}"
    return os.path.join('processed', str(instance.crop_image.user.id), name)


# ──────────────────────────────────────────────────────────────
# 🌾 CROP IMAGE MODEL
# Stores uploaded crop photo metadata
# ──────────────────────────────────────────────────────────────
class CropImage(models.Model):

    CROP_CHOICES = [
        ('wheat',   'Wheat'),
        ('rice',    'Rice'),
        ('maize',   'Maize'),
        ('tomato',  'Tomato'),
        ('potato',  'Potato'),
        ('cotton',  'Cotton'),
        ('soybean', 'Soybean'),
        ('sugarcane','Sugarcane'),
        ('other',   'Other'),
        ('unknown', 'Auto Detect'),
    ]

    STATUS_CHOICES = [
        ('pending',    'Pending Analysis'),
        ('processing', 'Processing'),
        ('completed',  'Analysis Complete'),
        ('failed',     'Analysis Failed'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='crop_images'
    )
    image       = models.ImageField(upload_to=crop_image_path)
    crop_type   = models.CharField(max_length=20, choices=CROP_CHOICES, default='unknown')
    original_filename = models.CharField(max_length=255, blank=True)
    file_size   = models.PositiveIntegerField(null=True, blank=True, help_text='File size in bytes')
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes       = models.TextField(blank=True, help_text='Optional notes from user')
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table  = 'crop_images'
        ordering  = ['-uploaded_at']
        verbose_name = 'Crop Image'
        verbose_name_plural = 'Crop Images'

    def __str__(self):
        return f"{self.user.email} – {self.crop_type} – {self.uploaded_at.date()}"

    @property
    def image_url(self):
        return self.image.url if self.image else None

    @property
    def has_result(self):
        return hasattr(self, 'result')


# ──────────────────────────────────────────────────────────────
# 🧠 ANALYSIS RESULT MODEL
# Stores AI prediction output
# ──────────────────────────────────────────────────────────────
class AnalysisResult(models.Model):

    SEVERITY_CHOICES = [
        ('none',     'None (Healthy)'),
        ('low',      'Low'),
        ('moderate', 'Moderate'),
        ('high',     'High'),
        ('critical', 'Critical'),
    ]

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    crop_image      = models.OneToOneField(CropImage, on_delete=models.CASCADE, related_name='result')

    # ── Core Prediction ───────────────────────────────────────
    disease_name    = models.CharField(max_length=255)
    scientific_name = models.CharField(max_length=255, blank=True)
    is_healthy      = models.BooleanField(default=False)
    confidence_score= models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text='Confidence percentage 0–100'
    )
    severity        = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='none')

    # ── Explanation ───────────────────────────────────────────
    description     = models.TextField(blank=True, help_text='What disease was detected and why')
    symptoms        = models.TextField(blank=True, help_text='Observable symptoms description')
    cause           = models.TextField(blank=True, help_text='Causal agent or reason')

    # ── Treatment ─────────────────────────────────────────────
    chemical_treatment  = models.TextField(blank=True)
    organic_treatment   = models.TextField(blank=True)
    preventive_measures = models.TextField(blank=True)

    # ── Visual Output ─────────────────────────────────────────
    processed_image     = models.ImageField(
        upload_to=processed_image_path,
        blank=True, null=True,
        help_text='Heatmap or bounding box overlay image'
    )
    bounding_box        = models.JSONField(
        null=True, blank=True,
        help_text='{"x": 0.2, "y": 0.3, "width": 0.4, "height": 0.3}'
    )

    # ── Alternative Predictions ───────────────────────────────
    alternative_predictions = models.JSONField(
        null=True, blank=True,
        help_text='[{"disease": "X", "confidence": 5.2}, ...]'
    )

    # ── Model Metadata ────────────────────────────────────────
    model_version   = models.CharField(max_length=50, default='v1.0-placeholder')
    processing_time = models.FloatField(null=True, blank=True, help_text='Seconds taken for inference')
    analyzed_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = 'analysis_results'
        ordering  = ['-analyzed_at']
        verbose_name = 'Analysis Result'

    def __str__(self):
        return f"{self.disease_name} ({self.confidence_score:.1f}%) – {self.crop_image.user.email}"

    @property
    def processed_image_url(self):
        return self.processed_image.url if self.processed_image else None


# ──────────────────────────────────────────────────────────────
# 🦠 DISEASE LIBRARY
# Static reference table for known diseases
# ──────────────────────────────────────────────────────────────
class Disease(models.Model):
    name            = models.CharField(max_length=255, unique=True)
    scientific_name = models.CharField(max_length=255, blank=True)
    crop_type       = models.CharField(max_length=50)
    description     = models.TextField()
    symptoms        = models.TextField()
    cause           = models.TextField()
    chemical_treatment   = models.TextField()
    organic_treatment    = models.TextField()
    preventive_measures  = models.TextField()
    severity_level  = models.CharField(max_length=20, default='moderate')
    image           = models.ImageField(upload_to='disease_library/', blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'diseases'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.crop_type})"
