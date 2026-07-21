import pytest
from rest_framework import status

from apps.analytics.services import AnalyticsService
from apps.projects.services import ProjectService


@pytest.mark.django_db
class TestAnalyticsService:
    def test_user_dashboard(self, user):
        ProjectService.create_project(
            owner=user,
            data={"title": "P1", "description": "d", "visibility": "public", "status": "published"},
        )
        dashboard = AnalyticsService.get_user_dashboard(user)
        assert dashboard["total_projects"] == 1

    def test_admin_dashboard(self, admin_user):
        dashboard = AnalyticsService.get_admin_dashboard()
        assert "total_users" in dashboard
        assert "total_projects" in dashboard


@pytest.mark.django_db
class TestAnalyticsAPI:
    def test_user_dashboard(self, authenticated_client):
        response = authenticated_client.get("/api/v1/dashboard/user/")
        assert response.status_code == status.HTTP_200_OK
        assert "total_projects" in response.data

    def test_admin_dashboard(self, admin_client):
        response = admin_client.get("/api/v1/dashboard/admin/")
        assert response.status_code == status.HTTP_200_OK
        assert "total_users" in response.data

    def test_non_admin_cannot_access_admin_dashboard(self, authenticated_client):
        response = authenticated_client.get("/api/v1/dashboard/admin/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
