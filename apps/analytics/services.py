from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone

User = get_user_model()


class AnalyticsService:
    @staticmethod
    def get_user_dashboard(user):
        from apps.projects.models import Project, Comment
        from apps.activity_logs.models import ActivityLog

        projects = Project.objects.filter(owner=user)
        return {
            "total_projects": projects.count(),
            "total_downloads": projects.aggregate(total=Count("download_count"))[
                "total"
            ]
            or 0,
            "total_comments": Comment.objects.filter(project__owner=user).count(),
            "recent_activities": list(
                ActivityLog.objects.filter(user=user).values(
                    "activity_type", "description", "created_at"
                )[:10]
            ),
        }

    @staticmethod
    def get_admin_dashboard():
        from apps.projects.models import Project, Comment

        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        daily_registrations = (
            User.objects.filter(created_at__gte=thirty_days_ago)
            .extra(select={"date": "date(created_at)"})
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        daily_uploads = (
            Project.objects.filter(created_at__gte=thirty_days_ago)
            .extra(select={"date": "date(created_at)"})
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        return {
            "total_users": User.objects.count(),
            "total_projects": Project.objects.count(),
            "total_comments": Comment.objects.count(),
            "total_downloads": Project.objects.aggregate(total=Count("download_count"))[
                "total"
            ]
            or 0,
            "daily_registrations": list(daily_registrations),
            "daily_uploads": list(daily_uploads),
        }
