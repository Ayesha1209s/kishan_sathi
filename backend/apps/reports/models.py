"""
===============================================================
🌱 KISHAN SATHI – Reports Models
Stores generated PDF report metadata
===============================================================
"""

import uuid
import os
from django.db import models
from django.conf import settings


def report_path(instance, filename):
    ext  = filename.split('.')[-1]
    name = f"report_{uuid.uuid4().hex}.{ext}"
    return os.path.join('reports', str(instance.user.id), name)


class Report(models.Model):

    REPORT_TYPE_CHOICES = [
        ('single',   'Single Analysis Report'),
        ('summary',  'Monthly Summary Report'),
        ('full',     'Full History Report'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports'
    )
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, default='single')
    title       = models.CharField(max_length=255)
    pdf_file    = models.FileField(upload_to=report_path, blank=True, null=True)
    # Link to single crop image (for 'single' type reports)
    crop_image  = models.ForeignKey(
        'analysis.CropImage',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reports'
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = 'reports'
        ordering  = ['-created_at']

    def __str__(self):
        return f"{self.report_type} – {self.user.email} – {self.created_at.date()}"

    @property
    def pdf_url(self):
        return self.pdf_file.url if self.pdf_file else None
