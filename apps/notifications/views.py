from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import FeedbackSerializer, NotificationSerializer
from .services import FeedbackService, NotificationService


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        unread_only = self.request.query_params.get("unread_only", "false") == "true"
        return NotificationService.get_user_notifications(
            self.request.user, unread_only=unread_only
        )

    @action(detail=True, methods=["patch"])
    def mark_read(self, request, pk=None):
        success = NotificationService.mark_as_read(pk, request.user)
        if success:
            return Response({"message": "Marked as read"})
        return Response(
            {"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=["patch"])
    def mark_all_read(self, request):
        count = NotificationService.mark_all_read(request.user)
        return Response({"message": f"Marked {count} notifications as read"})

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = NotificationService.get_unread_count(request.user)
        return Response({"count": count})


class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "delete"]

    def get_queryset(self):
        unread_only = self.request.query_params.get("unread_only", "false") == "true"
        return FeedbackService.get_user_feedbacks(
            self.request.user, unread_only=unread_only
        )

    @action(detail=True, methods=["patch"])
    def mark_read(self, request, pk=None):
        success = FeedbackService.mark_as_read(pk, request.user)
        if success:
            return Response({"message": "Marked as read"})
        return Response(
            {"error": "Feedback not found"}, status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=False, methods=["patch"])
    def mark_all_read(self, request):
        count = FeedbackService.mark_all_read(request.user)
        return Response({"message": f"Marked {count} feedback messages as read"})

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = FeedbackService.get_unread_count(request.user)
        return Response({"count": count})
