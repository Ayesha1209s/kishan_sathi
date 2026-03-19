"""
===============================================================
🌱 KISHAN SATHI – Accounts Models
Custom User model + Profile
===============================================================
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import os


def profile_image_path(instance, filename):
    """Dynamic upload path: media/profiles/<user_id>/<filename>"""
    ext  = filename.split('.')[-1]
    name = f"profile_{instance.user.id}.{ext}"
    return os.path.join('profiles', str(instance.user.id), name)


# ──────────────────────────────────────────────────────────────
# 👤 CUSTOM USER MODEL
# ──────────────────────────────────────────────────────────────
class User(AbstractUser):
    """
    Extended Django User with extra fields for Kishan Sathi.
    Using email as primary login identifier.
    """

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone: '+999999999'. Up to 15 digits."
    )

    email       = models.EmailField(unique=True, db_index=True)
    phone       = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    state       = models.CharField(max_length=100, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    # Use email as the login field
    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table  = 'users'
        ordering  = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name() or self.username} <{self.email}>"

    @property
    def total_analyses(self):
        return self.crop_images.count()


# ──────────────────────────────────────────────────────────────
# 🧑‍🌾 USER PROFILE MODEL
# ──────────────────────────────────────────────────────────────
class Profile(models.Model):
    """Extended profile info for each user."""

    EXPERIENCE_CHOICES = [
        ('beginner',      'Beginner (< 2 years)'),
        ('intermediate',  'Intermediate (2–10 years)'),
        ('experienced',   'Experienced (10+ years)'),
    ]

    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to=profile_image_path, blank=True, null=True)
    bio           = models.TextField(max_length=500, blank=True)
    experience    = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='beginner')
    farm_size     = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
                                        help_text='Farm size in acres')
    primary_crops = models.CharField(max_length=255, blank=True,
                                      help_text='Comma-separated crop names')
    district      = models.CharField(max_length=100, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'Profile'

    def __str__(self):
        return f"Profile of {self.user.email}"

    @property
    def profile_image_url(self):
        if self.profile_image:
            return self.profile_image.url
        return None


# ──────────────────────────────────────────────────────────────
# 🚫 BLACKLISTED TOKENS (extra safety layer)
# ──────────────────────────────────────────────────────────────
class UserActivity(models.Model):
    """Track login/logout events for security audit."""

    ACTION_CHOICES = [
        ('login',    'Login'),
        ('logout',   'Logout'),
        ('register', 'Register'),
        ('password_change', 'Password Change'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action     = models.CharField(max_length=30, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = 'user_activities'
        ordering  = ['-timestamp']
        verbose_name_plural = 'User Activities'

    def __str__(self):
        return f"{self.user.email} – {self.action} at {self.timestamp}"
