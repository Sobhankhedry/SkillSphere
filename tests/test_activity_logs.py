import pytest
from rest_framework import status

from apps.activity_logs.models import ActivityLog
from apps.activity_logs.services import ActivityLogService


@pytest.mark.django_db
class TestActivityLogService:
    def test_log_activity(self, user):
        log = ActivityLogService.log_activity(
            user=user,
            activity_type="login",
            description="User logged in",
            ip_address="127.0.0.1",
        )
        assert log.user == user
        assert log.activity_type == "login"

    def test_get_user_activities(self, user):
        ActivityLogService.log_activity(user=user, activity_type="login", description="Login")
        ActivityLogService.log_activity(user=user, activity_type="logout", description="Logout")
        activities = ActivityLogService.get_user_activities(user)
        assert len(activities) == 2

    def test_get_recent_activities(self, user):
        ActivityLogService.log_activity(user=user, activity_type="login", description="Login")
        activities = ActivityLogService.get_recent_activities()
        assert len(activities) >= 1


@pytest.mark.django_db
class TestActivityLogAPI:
    def test_list_own_activities(self, authenticated_client, user):
        ActivityLogService.log_activity(user=user, activity_type="login", description="Login")
        response = authenticated_client.get("/api/v1/activity-logs/")
        assert response.status_code == status.HTTP_200_OK

    def test_unauthenticated_cannot_list(self, api_client):
        response = api_client.get("/api/v1/activity-logs/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_admin_sees_all_activities(self, admin_client, user):
        ActivityLogService.log_activity(user=user, activity_type="login", description="Login")
        response = admin_client.get("/api/v1/activity-logs/")
        assert response.status_code == status.HTTP_200_OK
