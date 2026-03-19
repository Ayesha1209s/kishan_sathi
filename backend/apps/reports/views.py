"""
===============================================================
🌱 KISHAN SATHI – Reports Views
Generate and download PDF reports (single + summary)
===============================================================
"""

import os
import logging
from django.http import HttpResponse, Http404
from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analysis.models import CropImage
from .models import Report
from .serializers import ReportSerializer
from .pdf_generator import generate_single_analysis_pdf, generate_summary_pdf
from apps.notifications.utils import create_notification

logger = logging.getLogger('apps.reports')


# ──────────────────────────────────────────────────────────────
# 📄 GENERATE SINGLE ANALYSIS REPORT
# POST /api/v1/reports/generate/<crop_image_id>/
# ──────────────────────────────────────────────────────────────
class GenerateSingleReportView(APIView):
    """
    Generates a PDF for a specific analysis and returns download URL.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        # Validate ownership + result exists
        try:
            crop_image = CropImage.objects.select_related('result').get(
                id=pk, user=request.user, status='completed'
            )
        except CropImage.DoesNotExist:
            return Response(
                {'error': 'Completed analysis not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not crop_image.has_result:
            return Response(
                {'error': 'No analysis result available for this image.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Generate PDF bytes
            pdf_bytes = generate_single_analysis_pdf(
                user       = request.user,
                crop_image = crop_image,
                result     = crop_image.result,
            )

            # Save to Report model
            report = Report(
                user        = request.user,
                report_type = 'single',
                title       = f"Crop Analysis – {crop_image.result.disease_name} – {timezone.now().strftime('%d %b %Y')}",
                crop_image  = crop_image,
            )
            filename = f"crop_analysis_{str(crop_image.id)[:8]}.pdf"
            report.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)

            create_notification(
                user              = request.user,
                notification_type = 'report_ready',
                title             = 'Report Ready',
                message           = f'Your PDF report for {crop_image.result.disease_name} is ready to download.',
                related_image     = crop_image,
            )

            logger.info(f"Report generated: {report.id} for user {request.user.email}")

            return Response({
                'message':    'PDF report generated successfully.',
                'report_id':  str(report.id),
                'pdf_url':    request.build_absolute_uri(report.pdf_url),
                'title':      report.title,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"PDF generation failed: {e}", exc_info=True)
            return Response(
                {'error': 'Failed to generate PDF. Ensure reportlab is installed.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ──────────────────────────────────────────────────────────────
# 📊 GENERATE SUMMARY REPORT
# POST /api/v1/reports/generate-summary/?period=30
# ──────────────────────────────────────────────────────────────
class GenerateSummaryReportView(APIView):
    """Generates a multi-analysis summary PDF for the given period."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from datetime import timedelta
        period = int(request.query_params.get('period', 30))
        period = min(max(period, 7), 365)

        since = timezone.now() - timedelta(days=period)
        images = CropImage.objects.filter(
            user=request.user,
            status='completed',
            uploaded_at__gte=since,
        ).select_related('result').order_by('-uploaded_at')

        if not images.exists():
            return Response(
                {'error': f'No completed analyses found in the last {period} days.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            period_label = f"Last {period} Days"
            pdf_bytes    = generate_summary_pdf(request.user, list(images), period_label)

            report = Report(
                user        = request.user,
                report_type = 'summary',
                title       = f"Summary Report – {period_label} – {timezone.now().strftime('%d %b %Y')}",
            )
            filename = f"summary_{request.user.id}_{timezone.now().strftime('%Y%m%d')}.pdf"
            report.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)

            return Response({
                'message':    'Summary PDF generated.',
                'report_id':  str(report.id),
                'pdf_url':    request.build_absolute_uri(report.pdf_url),
                'analyses':   images.count(),
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Summary PDF generation failed: {e}", exc_info=True)
            return Response({'error': 'Failed to generate summary PDF.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ──────────────────────────────────────────────────────────────
# ⬇️ DOWNLOAD PDF INLINE
# GET /api/v1/reports/download/<report_id>/
# ──────────────────────────────────────────────────────────────
class DownloadReportView(APIView):
    """Streams PDF file as an HTTP response for direct browser download."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            report = Report.objects.get(id=pk, user=request.user)
        except Report.DoesNotExist:
            raise Http404("Report not found.")

        if not report.pdf_file:
            return Response({'error': 'PDF file missing.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            with open(report.pdf_file.path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='application/pdf')
                filename = os.path.basename(report.pdf_file.name)
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
        except FileNotFoundError:
            return Response({'error': 'PDF file not found on server.'}, status=status.HTTP_404_NOT_FOUND)


# ──────────────────────────────────────────────────────────────
# 📂 LIST USER REPORTS
# GET /api/v1/reports/
# ──────────────────────────────────────────────────────────────
class ReportListView(generics.ListAPIView):
    """List all generated reports for the current user."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = ReportSerializer

    def get_queryset(self):
        return Report.objects.filter(user=self.request.user)
