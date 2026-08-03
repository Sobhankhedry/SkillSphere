from django.contrib.auth import get_user_model

from .models import ActivityLog

User = get_user_model()


class ActivityLogService:
    @staticmethod
    def log_activity(
        user,
        activity_type: str,
        description: str = "",
        ip_address: str = None,
        user_agent: str = "",
        metadata: dict = None,
    ) -> ActivityLog:
        return ActivityLog.objects.create(
            user=user,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
        )

    @staticmethod
    def get_user_activities(user: User, activity_type: str = None):
        queryset = ActivityLog.objects.filter(user=user)
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        return queryset[:50]

    @staticmethod
    def get_recent_activities(limit: int = 10):
        return ActivityLog.objects.select_related("user")[:limit]
