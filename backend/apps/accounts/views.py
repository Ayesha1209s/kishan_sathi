"""
===============================================================
🌱 KISHAN SATHI – Accounts Views
Registration, Login, Logout, Profile, Password Change
===============================================================
"""

import logging
from django.contrib.auth import get_user_model
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import Profile, UserActivity
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    UserActivitySerializer,
)

logger = logging.getLogger('apps.accounts')
User   = get_user_model()


def get_client_ip(request):
    """Extract real client IP from request headers."""
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# ──────────────────────────────────────────────────────────────
# 📝 REGISTER VIEW
# POST /api/v1/auth/register/
# ──────────────────────────────────────────────────────────────
class RegisterView(generics.CreateAPIView):
    """
    Public endpoint. Creates new user + profile.
    Returns JWT access + refresh tokens on success.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class   = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Log activity
        UserActivity.objects.create(
            user=user, action='register',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        logger.info(f"New user registered: {user.email}")

        return Response({
            'message': 'Registration successful! Welcome to Kishan Sathi.',
            'tokens': {
                'access':  str(refresh.access_token),
                'refresh': str(refresh),
            },
            'user': {
                'id':       user.id,
                'username': user.username,
                'email':    user.email,
                'full_name': user.get_full_name(),
            }
        }, status=status.HTTP_201_CREATED)


# ──────────────────────────────────────────────────────────────
# 🔑 LOGIN VIEW
# POST /api/v1/auth/login/
# ──────────────────────────────────────────────────────────────
class LoginView(TokenObtainPairView):
    """
    JWT login. Returns access + refresh tokens with user data.
    Uses email as USERNAME_FIELD.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class   = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Log successful login
            email = request.data.get('email', '')
            try:
                user = User.objects.get(email=email)
                UserActivity.objects.create(
                    user=user, action='login',
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                logger.info(f"User logged in: {email}")
            except User.DoesNotExist:
                pass

        return response


# ──────────────────────────────────────────────────────────────
# 🚪 LOGOUT VIEW
# POST /api/v1/auth/logout/
# ──────────────────────────────────────────────────────────────
class LogoutView(APIView):
    """
    Blacklists the refresh token to invalidate the session.
    Requires: { "refresh": "<refresh_token>" }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()

            UserActivity.objects.create(
                user=request.user, action='logout',
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            logger.info(f"User logged out: {request.user.email}")

            return Response({'message': 'Logged out successfully.'}, status=status.HTTP_200_OK)

        except TokenError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────────────────────────
# 👤 PROFILE VIEW
# GET/PUT/PATCH /api/v1/auth/profile/
# ──────────────────────────────────────────────────────────────
class ProfileView(generics.RetrieveUpdateAPIView):
    """Get or update the authenticated user's profile."""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserDetailSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True  # Always allow partial updates
        response = super().update(request, *args, **kwargs)
        response.data['message'] = 'Profile updated successfully.'
        return response


# ──────────────────────────────────────────────────────────────
# 🖼️ PROFILE IMAGE UPLOAD
# POST /api/v1/auth/profile/image/
# ──────────────────────────────────────────────────────────────
class ProfileImageUploadView(APIView):
    """Dedicated endpoint for profile image upload."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile = request.user.profile
        image   = request.FILES.get('profile_image')

        if not image:
            return Response({'error': 'No image provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file type
        allowed = ['image/jpeg', 'image/png', 'image/webp']
        if image.content_type not in allowed:
            return Response({'error': 'Only JPG, PNG, WEBP allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file size (2MB max for profile)
        if image.size > 2 * 1024 * 1024:
            return Response({'error': 'Profile image must be under 2MB.'}, status=status.HTTP_400_BAD_REQUEST)

        profile.profile_image = image
        profile.save()

        return Response({
            'message': 'Profile image updated.',
            'image_url': profile.profile_image_url
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────────────────────
# 🔑 CHANGE PASSWORD
# POST /api/v1/auth/change-password/
# ──────────────────────────────────────────────────────────────
class ChangePasswordView(APIView):
    """Change authenticated user's password."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        UserActivity.objects.create(
            user=user, action='password_change',
            ip_address=get_client_ip(request),
        )

        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────────────────────
# 📋 USER ACTIVITY
# GET /api/v1/auth/activity/
# ──────────────────────────────────────────────────────────────
class UserActivityView(generics.ListAPIView):
    """List login/logout activity for the current user."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = UserActivitySerializer

    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)[:20]


# ──────────────────────────────────────────────────────────────
# 📊 DASHBOARD SUMMARY
# GET /api/v1/auth/dashboard/
# ──────────────────────────────────────────────────────────────
class UserDashboardView(APIView):
    """Returns summary stats for the authenticated user's dashboard."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from apps.analysis.models import CropImage, AnalysisResult

        user        = request.user
        all_images  = CropImage.objects.filter(user=user)
        all_results = AnalysisResult.objects.filter(crop_image__user=user)

        total_uploads  = all_images.count()
        disease_count  = all_results.filter(is_healthy=False).count()
        healthy_count  = all_results.filter(is_healthy=True).count()
        avg_confidence = all_results.aggregate(
            avg=__import__('django.db.models', fromlist=['Avg']).Avg('confidence_score')
        )['avg'] or 0

        # Recent 5 uploads
        from apps.analysis.serializers import CropImageListSerializer
        recent = CropImage.objects.filter(user=user).order_by('-uploaded_at')[:5]

        return Response({
            'user': {
                'name':  user.get_full_name() or user.username,
                'email': user.email,
            },
            'stats': {
                'total_uploads':    total_uploads,
                'diseases_found':   disease_count,
                'healthy_crops':    healthy_count,
                'avg_confidence':   round(float(avg_confidence), 2),
                'success_rate':     round(
                    (all_results.count() / total_uploads * 100) if total_uploads else 0, 1
                ),
            },
            'recent_activity': CropImageListSerializer(recent, many=True, context={'request': request}).data,
        })
