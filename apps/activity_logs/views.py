from rest_framework import permissions, viewsets
from rest_framework.response import Response

from .models import ActivityLog
from .serializers import ActivityLogSerializer
from .services import ActivityLogService


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) == "admin":
            return ActivityLog.objects.select_related("user").all()
        return ActivityLog.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        activity_type = request.query_params.get("type")
        activities = ActivityLogService.get_user_activities(
            request.user, activity_type=activity_type
        )
        serializer = self.get_serializer(activities, many=True)
        return Response(serializer.data)
