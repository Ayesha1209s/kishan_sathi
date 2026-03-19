"""
===============================================================
🌱 KISHAN SATHI – Notification Utilities
Helper function to create notifications from anywhere in the app
===============================================================
"""

import logging
from .models import Notification

logger = logging.getLogger('apps.notifications')


def create_notification(user, notification_type, title, message, related_image=None):
    """
    Create an in-app notification for a user.
    Called from analysis views, report views, etc.
    """
    try:
        notif = Notification.objects.create(
            user              = user,
            notification_type = notification_type,
            title             = title,
            message           = message,
            related_image_id  = related_image.id if related_image else None,
        )
        logger.info(f"Notification created for {user.email}: {title}")
        return notif
    except Exception as e:
        logger.error(f"Failed to create notification: {e}")
        return None
