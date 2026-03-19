"""
===============================================================
🌱 KISHAN SATHI – Notifications Models
In-app notification storage and management
===============================================================
"""

import uuid
from django.db import models
from django.conf import settings


class Notification(models.Model):

    TYPE_CHOICES = [
        ('analysis_complete', 'Analysis Complete'),
        ('disease_alert',     'Disease Alert'),
        ('system',            'System Announcement'),
        ('report_ready',      'Report Ready'),
        ('welcome',           'Welcome'),
    ]

    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user              = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='system')
    title             = models.CharField(max_length=255)
    message           = models.TextField()
    is_read           = models.BooleanField(default=False, db_index=True)
    related_image_id  = models.UUIDField(null=True, blank=True)  # Optional FK to CropImage
    created_at        = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table  = 'notifications'
        ordering  = ['-created_at']
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"[{self.notification_type}] {self.user.email}: {self.title}"
