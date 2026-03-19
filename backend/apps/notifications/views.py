"""
===============================================================
🌱 KISHAN SATHI – Notifications Views
List, mark-read, delete notifications
===============================================================
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


# ── List all notifications ────────────────────────────────────
# GET /api/v1/notifications/
class NotificationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        qs       = self.get_queryset()
        unread   = qs.filter(is_read=False).count()
        page     = self.paginate_queryset(qs)
        data     = self.get_serializer(page, many=True).data
        response = self.get_paginated_response(data)
        response.data['unread_count'] = unread
        return response


# ── Mark single notification as read ─────────────────────────
# PATCH /api/v1/notifications/<id>/read/
class MarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            notif = Notification.objects.get(id=pk, user=request.user)
            notif.is_read = True
            notif.save(update_fields=['is_read'])
            return Response({'message': 'Marked as read.'})
        except Notification.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)


# ── Mark all notifications as read ───────────────────────────
# POST /api/v1/notifications/mark-all-read/
class MarkAllReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        return Response({'message': f'{count} notifications marked as read.'})


# ── Delete a notification ─────────────────────────────────────
# DELETE /api/v1/notifications/<id>/
class NotificationDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({'message': 'Notification deleted.'}, status=status.HTTP_200_OK)


# ── Unread count ──────────────────────────────────────────────
# GET /api/v1/notifications/unread-count/
class UnreadCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})
