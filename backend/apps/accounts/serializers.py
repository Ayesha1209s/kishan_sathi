"""
===============================================================
🌱 KISHAN SATHI – Accounts Serializers
User Registration, Login, Profile serializers
===============================================================
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Profile, UserActivity

User = get_user_model()


# ──────────────────────────────────────────────────────────────
# 🎟️ CUSTOM JWT TOKEN SERIALIZER
# Adds extra user info to the token response
# ──────────────────────────────────────────────────────────────
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Returns JWT token pair with extra user data embedded."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Embed non-sensitive data into token payload
        token['username']    = user.username
        token['email']       = user.email
        token['full_name']   = user.get_full_name()
        token['is_verified'] = user.is_verified
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Append user details to response
        data['user'] = {
            'id':           self.user.id,
            'username':     self.user.username,
            'email':        self.user.email,
            'full_name':    self.user.get_full_name(),
            'is_verified':  self.user.is_verified,
            'total_analyses': self.user.total_analyses,
        }
        return data


# ──────────────────────────────────────────────────────────────
# 📝 USER REGISTRATION SERIALIZER
# ──────────────────────────────────────────────────────────────
class UserRegistrationSerializer(serializers.ModelSerializer):
    """Handles new user registration with password confirmation."""

    password         = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model  = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone', 'state', 'password', 'confirm_password'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name':  {'required': True},
            'email':      {'required': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        # Auto-create linked profile
        Profile.objects.create(user=user)
        return user


# ──────────────────────────────────────────────────────────────
# 🧑‍🌾 PROFILE SERIALIZER
# ──────────────────────────────────────────────────────────────
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Profile
        fields = [
            'id', 'bio', 'experience', 'farm_size',
            'primary_crops', 'district', 'profile_image',
            'profile_image_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'profile_image_url']


# ──────────────────────────────────────────────────────────────
# 👤 USER DETAIL SERIALIZER
# ──────────────────────────────────────────────────────────────
class UserDetailSerializer(serializers.ModelSerializer):
    """Full user info including nested profile."""

    profile         = ProfileSerializer(read_only=True)
    total_analyses  = serializers.ReadOnlyField()

    class Meta:
        model  = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'state', 'is_verified', 'total_analyses',
            'profile', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'email', 'is_verified', 'created_at', 'updated_at']


# ──────────────────────────────────────────────────────────────
# ✏️ USER UPDATE SERIALIZER
# ──────────────────────────────────────────────────────────────
class UserUpdateSerializer(serializers.ModelSerializer):
    """Update user + profile fields in one request."""

    profile = ProfileSerializer(required=False)

    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'phone', 'state', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile fields
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


# ──────────────────────────────────────────────────────────────
# 🔑 CHANGE PASSWORD SERIALIZER
# ──────────────────────────────────────────────────────────────
class ChangePasswordSerializer(serializers.Serializer):
    old_password     = serializers.CharField(required=True, write_only=True)
    new_password     = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "New passwords do not match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


# ──────────────────────────────────────────────────────────────
# 📋 USER ACTIVITY SERIALIZER
# ──────────────────────────────────────────────────────────────
class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserActivity
        fields = ['id', 'action', 'ip_address', 'timestamp']
        read_only_fields = fields
