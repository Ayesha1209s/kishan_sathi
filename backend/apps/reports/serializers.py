from rest_framework import serializers
from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    pdf_url = serializers.ReadOnlyField()

    class Meta:
        model  = Report
        fields = ['id', 'report_type', 'title', 'pdf_url', 'crop_image', 'created_at']
        read_only_fields = fields
