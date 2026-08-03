import pytest
from rest_framework import status

from apps.notifications.models import Notification
from apps.notifications.services import NotificationService


@pytest.mark.django_db
class TestNotificationService:
    def test_create_notification(self, user):
        notification = NotificationService.create_notification(
            recipient=user,
            notification_type="system_message",
            title="Welcome",
            message="Welcome to SkillSphere!",
        )
        assert notification.recipient == user
        assert notification.is_read is False

    def test_mark_as_read(self, user):
        notification = NotificationService.create_notification(
            recipient=user,
            notification_type="system_message",
            title="Test",
            message="Test message",
        )
        result = NotificationService.mark_as_read(str(notification.id), user)
        assert result is True
        notification.refresh_from_db()
        assert notification.is_read is True

    def test_mark_all_read(self, user):
        for i in range(3):
            NotificationService.create_notification(
                recipient=user,
                notification_type="system_message",
                title=f"Test {i}",
                message=f"Message {i}",
            )
        count = NotificationService.mark_all_read(user)
        assert count == 3
        assert Notification.objects.filter(recipient=user, is_read=False).count() == 0

    def test_get_unread_count(self, user):
        NotificationService.create_notification(
            recipient=user,
            notification_type="system_message",
            title="Unread",
            message="msg",
        )
        assert NotificationService.get_unread_count(user) == 1


@pytest.mark.django_db
class TestNotificationAPI:
    def test_list_notifications(self, authenticated_client, user):
        NotificationService.create_notification(
            recipient=user,
            notification_type="system_message",
            title="Test",
            message="msg",
        )
        response = authenticated_client.get("/api/v1/notifications/")
        assert response.status_code == status.HTTP_200_OK

    def test_unread_count(self, authenticated_client, user):
        NotificationService.create_notification(
            recipient=user,
            notification_type="system_message",
            title="Test",
            message="msg",
        )
        response = authenticated_client.get("/api/v1/notifications/unread_count/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_mark_read(self, authenticated_client, user):
        notification = NotificationService.create_notification(
            recipient=user,
            notification_type="system_message",
            title="Test",
            message="msg",
        )
        response = authenticated_client.patch(
            f"/api/v1/notifications/{notification.id}/mark_read/"
        )
        assert response.status_code == status.HTTP_200_OK
