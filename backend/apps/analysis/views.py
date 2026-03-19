"""
===============================================================
🌱 KISHAN SATHI – Analysis Views
Image Upload, AI Analysis, History, Search, Analytics
===============================================================
"""

import logging
from datetime import timedelta

from django.utils import timezone
from django.db.models import Count, Avg, Q
from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
import django_filters

from .models import CropImage, AnalysisResult, Disease
from .serializers import (
    CropImageUploadSerializer,
    CropImageListSerializer,
    CropImageDetailSerializer,
    AnalysisResultSerializer,
    AnalyticsSerializer,
    DiseaseSerializer,
)
from .ai_service import run_analysis
from apps.notifications.utils import create_notification

logger = logging.getLogger('apps.analysis')


# ──────────────────────────────────────────────────────────────
# 🔎 FILTER CLASS
# ──────────────────────────────────────────────────────────────
class CropImageFilter(django_filters.FilterSet):
    """Filter crop images by date range, crop type, disease, status."""

    uploaded_after  = django_filters.DateFilter(field_name='uploaded_at', lookup_expr='gte')
    uploaded_before = django_filters.DateFilter(field_name='uploaded_at', lookup_expr='lte')
    disease         = django_filters.CharFilter(field_name='result__disease_name', lookup_expr='icontains')
    is_healthy      = django_filters.BooleanFilter(field_name='result__is_healthy')
    min_confidence  = django_filters.NumberFilter(field_name='result__confidence_score', lookup_expr='gte')

    class Meta:
        model  = CropImage
        fields = ['crop_type', 'status', 'uploaded_after', 'uploaded_before',
                  'disease', 'is_healthy', 'min_confidence']


# ──────────────────────────────────────────────────────────────
# 📷 IMAGE UPLOAD VIEW
# POST /api/v1/analysis/upload/
# ──────────────────────────────────────────────────────────────
class CropImageUploadView(generics.CreateAPIView):
    """
    Upload a crop image. After upload, call /analyze/<id>/ to run AI.
    Accepts multipart/form-data with 'image' field.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = CropImageUploadSerializer
    parser_classes     = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        logger.info(f"Image uploaded: user={request.user.email}, id={serializer.data['id']}")

        return Response({
            'message': 'Image uploaded successfully. Call /analyze/ to run AI detection.',
            'upload':  serializer.data,
        }, status=status.HTTP_201_CREATED)


# ──────────────────────────────────────────────────────────────
# 🔬 AI ANALYZE VIEW
# POST /api/v1/analysis/analyze/<id>/
# ──────────────────────────────────────────────────────────────
class AnalyzeView(APIView):
    """
    Runs the AI model on a previously uploaded image.
    Creates/updates the linked AnalysisResult.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        # Verify ownership
        try:
            crop_image = CropImage.objects.get(id=pk, user=request.user)
        except CropImage.DoesNotExist:
            return Response({'error': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)

        if crop_image.status == 'processing':
            return Response({'error': 'Analysis already in progress.'}, status=status.HTTP_409_CONFLICT)

        # Mark as processing
        crop_image.status = 'processing'
        crop_image.save(update_fields=['status'])

        try:
            # Run AI inference
            image_path = crop_image.image.path
            prediction = run_analysis(image_path)

            # Save result to DB
            result, created = AnalysisResult.objects.update_or_create(
                crop_image=crop_image,
                defaults={
                    'disease_name':             prediction['disease_name'],
                    'scientific_name':          prediction.get('scientific_name', ''),
                    'is_healthy':               prediction['is_healthy'],
                    'confidence_score':         prediction['confidence_score'],
                    'severity':                 prediction.get('severity', 'moderate'),
                    'description':              prediction.get('description', ''),
                    'symptoms':                 prediction.get('symptoms', ''),
                    'cause':                    prediction.get('cause', ''),
                    'chemical_treatment':       prediction.get('chemical_treatment', ''),
                    'organic_treatment':        prediction.get('organic_treatment', ''),
                    'preventive_measures':      prediction.get('preventive_measures', ''),
                    'alternative_predictions':  prediction.get('alternative_predictions', []),
                    'model_version':            prediction.get('model_version', 'v1.0'),
                    'processing_time':          prediction.get('processing_time', 0),
                }
            )

            # Mark image as complete
            crop_image.status = 'completed'
            crop_image.save(update_fields=['status'])

            # Send notification
            msg = (
                f"✅ Healthy crop detected with {result.confidence_score:.1f}% confidence."
                if result.is_healthy else
                f"⚠️ {result.disease_name} detected with {result.confidence_score:.1f}% confidence."
            )
            create_notification(
                user=request.user,
                notification_type='analysis_complete',
                title='Analysis Complete',
                message=msg,
                related_image=crop_image,
            )

            # Send email (async in production)
            try:
                from .utils import send_analysis_email
                send_analysis_email(request.user, crop_image, result)
            except Exception as e:
                logger.warning(f"Email send failed (non-fatal): {e}")

            logger.info(
                f"Analysis saved: id={crop_image.id}, disease={result.disease_name}, "
                f"conf={result.confidence_score:.1f}%"
            )

            return Response({
                'message': 'Analysis complete.',
                'result':  AnalysisResultSerializer(result, context={'request': request}).data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            crop_image.status = 'failed'
            crop_image.save(update_fields=['status'])
            logger.error(f"Analysis failed for image {pk}: {e}", exc_info=True)
            return Response(
                {'error': 'Analysis failed. Please try with a clearer image.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ──────────────────────────────────────────────────────────────
# ⚡ UPLOAD + ANALYZE IN ONE STEP
# POST /api/v1/analysis/upload-analyze/
# ──────────────────────────────────────────────────────────────
class UploadAndAnalyzeView(APIView):
    """
    Convenience endpoint: upload image AND run AI in one request.
    Perfect for the frontend's single "Analyze" button.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request):
        # Step 1: Validate & upload
        upload_serializer = CropImageUploadSerializer(data=request.data, context={'request': request})
        upload_serializer.is_valid(raise_exception=True)
        crop_image = upload_serializer.save(user=request.user)

        # Step 2: Mark as processing
        crop_image.status = 'processing'
        crop_image.save(update_fields=['status'])

        try:
            # Step 3: Run AI
            prediction = run_analysis(crop_image.image.path)

            # Step 4: Save result
            result = AnalysisResult.objects.create(
                crop_image      = crop_image,
                disease_name    = prediction['disease_name'],
                scientific_name = prediction.get('scientific_name', ''),
                is_healthy      = prediction['is_healthy'],
                confidence_score= prediction['confidence_score'],
                severity        = prediction.get('severity', 'none'),
                description     = prediction.get('description', ''),
                symptoms        = prediction.get('symptoms', ''),
                cause           = prediction.get('cause', ''),
                chemical_treatment   = prediction.get('chemical_treatment', ''),
                organic_treatment    = prediction.get('organic_treatment', ''),
                preventive_measures  = prediction.get('preventive_measures', ''),
                alternative_predictions = prediction.get('alternative_predictions', []),
                model_version        = prediction.get('model_version', 'v1.0'),
                processing_time      = prediction.get('processing_time', 0),
            )

            crop_image.status = 'completed'
            crop_image.save(update_fields=['status'])

            # Notify user
            msg = (
                f"✅ Healthy crop! Confidence: {result.confidence_score:.1f}%"
                if result.is_healthy else
                f"⚠️ {result.disease_name} detected. Confidence: {result.confidence_score:.1f}%"
            )
            create_notification(request.user, 'analysis_complete', 'Analysis Complete', msg, crop_image)

            return Response({
                'message':    'Upload and analysis complete.',
                'image_id':   str(crop_image.id),
                'image_url':  crop_image.image_url,
                'result':     AnalysisResultSerializer(result, context={'request': request}).data,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            crop_image.status = 'failed'
            crop_image.save(update_fields=['status'])
            logger.error(f"Upload+analyze failed: {e}", exc_info=True)
            return Response({'error': 'Analysis failed. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ──────────────────────────────────────────────────────────────
# 📂 HISTORY LIST VIEW
# GET /api/v1/analysis/history/
# ──────────────────────────────────────────────────────────────
class HistoryListView(generics.ListAPIView):
    """
    Paginated history of user's uploads.
    Supports search, filtering by date/disease/crop, ordering.
    """
    permission_classes  = [permissions.IsAuthenticated]
    serializer_class    = CropImageListSerializer
    filter_backends     = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class     = CropImageFilter
    search_fields       = ['result__disease_name', 'crop_type', 'original_filename']
    ordering_fields     = ['uploaded_at', 'result__confidence_score']
    ordering            = ['-uploaded_at']

    def get_queryset(self):
        return CropImage.objects.filter(
            user=self.request.user
        ).select_related('result').order_by('-uploaded_at')


# ──────────────────────────────────────────────────────────────
# 🔍 HISTORY DETAIL VIEW
# GET/DELETE /api/v1/analysis/history/<id>/
# ──────────────────────────────────────────────────────────────
class HistoryDetailView(generics.RetrieveDestroyAPIView):
    """Get or delete a specific analysis record."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = CropImageDetailSerializer

    def get_queryset(self):
        return CropImage.objects.filter(
            user=self.request.user
        ).select_related('result')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'Analysis record deleted.'}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────────────────────
# 📈 ANALYTICS VIEW
# GET /api/v1/analysis/analytics/?period=7  (7 | 30 | 90 days)
# ──────────────────────────────────────────────────────────────
class AnalyticsView(APIView):
    """Dashboard analytics: total uploads, disease breakdown, daily chart data."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        period = int(request.query_params.get('period', 30))
        period = min(max(period, 7), 365)  # Clamp 7–365

        since  = timezone.now() - timedelta(days=period)
        qs     = CropImage.objects.filter(user=request.user, uploaded_at__gte=since)
        res_qs = AnalysisResult.objects.filter(crop_image__user=request.user, analyzed_at__gte=since)

        total_uploads  = qs.count()
        diseases_found = res_qs.filter(is_healthy=False).count()
        healthy_crops  = res_qs.filter(is_healthy=True).count()
        avg_conf       = res_qs.aggregate(avg=Avg('confidence_score'))['avg'] or 0

        # Daily upload counts
        from django.db.models.functions import TruncDate
        daily_data = list(
            qs.annotate(date=TruncDate('uploaded_at'))
              .values('date')
              .annotate(count=Count('id'))
              .order_by('date')
        )
        for d in daily_data:
            d['date'] = d['date'].isoformat()

        # Top 5 diseases
        top_diseases = list(
            res_qs.exclude(is_healthy=True)
                  .values('disease_name')
                  .annotate(count=Count('id'))
                  .order_by('-count')[:5]
        )

        return Response({
            'period':         period,
            'total_uploads':  total_uploads,
            'diseases_found': diseases_found,
            'healthy_crops':  healthy_crops,
            'avg_confidence': round(float(avg_conf), 2),
            'daily_data':     daily_data,
            'top_diseases':   top_diseases,
        })


# ──────────────────────────────────────────────────────────────
# 🦠 DISEASE LIBRARY
# GET /api/v1/analysis/diseases/
# ──────────────────────────────────────────────────────────────
class DiseaseLibraryView(generics.ListAPIView):
    """Public disease library — no auth required."""
    permission_classes = [permissions.AllowAny]
    serializer_class   = DiseaseSerializer
    queryset           = Disease.objects.all()
    filter_backends    = [filters.SearchFilter, DjangoFilterBackend]
    search_fields      = ['name', 'crop_type', 'scientific_name']
    filterset_fields   = ['crop_type', 'severity_level']
