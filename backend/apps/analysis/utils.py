"""
===============================================================
🌱 KISHAN SATHI – Analysis Email Utilities
Sends result notification emails to users
===============================================================
"""

import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger('apps.analysis')


def send_analysis_email(user, crop_image, result):
    """Send analysis result summary email to the user."""

    if not user.email:
        return

    status_emoji = "✅" if result.is_healthy else "⚠️"
    subject = f"{status_emoji} Kishan Sathi: Your Crop Analysis is Ready"

    body = f"""
Hello {user.get_full_name() or user.username},

Your crop analysis is complete! Here's a summary:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌾 ANALYSIS RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Crop Type:      {crop_image.get_crop_type_display()}
Diagnosis:      {result.disease_name}
Confidence:     {result.confidence_score:.1f}%
Severity:       {result.get_severity_display()}
Date:           {result.analyzed_at.strftime('%d %b %Y, %I:%M %p IST')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💊 RECOMMENDED ACTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{result.chemical_treatment or 'No chemical treatment required.'}

Log in to Kishan Sathi to view the full report and download your PDF.
http://kishansathi.in/dashboard

Stay vigilant, grow healthy! 🌱

— Team Kishan Sathi
"""

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        logger.info(f"Analysis email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send email to {user.email}: {e}")
