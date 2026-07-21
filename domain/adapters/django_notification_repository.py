from uuid import UUID

from apps.notifications.models import Notification
from domain.entities.notification import NotificationEntity
from domain.ports.notification_repository import NotificationRepository


def _to_entity(n: Notification) -> NotificationEntity:
    return NotificationEntity(
        id=n.id,
        recipient_id=n.recipient_id,
        notification_type=n.notification_type,
        title=n.title,
        message=n.message,
        sender_id=n.sender_id,
        link=n.link,
        is_read=n.is_read,
    )


class DjangoNotificationRepository(NotificationRepository):
    def create(self, entity: NotificationEntity) -> NotificationEntity:
        n = Notification.objects.create(
            recipient_id=entity.recipient_id,
            sender_id=entity.sender_id,
            notification_type=entity.notification_type,
            title=entity.title,
            message=entity.message,
            link=entity.link,
        )
        return _to_entity(n)

    def get_by_recipient(self, recipient_id: UUID, unread_only: bool = False) -> list[NotificationEntity]:
        qs = Notification.objects.filter(recipient_id=recipient_id)
        if unread_only:
            qs = qs.filter(is_read=False)
        return [_to_entity(n) for n in qs.order_by("-created_at")]

    def get_unread_count(self, recipient_id: UUID) -> int:
        return Notification.objects.filter(recipient_id=recipient_id, is_read=False).count()

    def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool:
        try:
            n = Notification.objects.get(id=notification_id, recipient_id=user_id)
            n.mark_read()
            return True
        except Notification.DoesNotExist:
            return False

    def mark_all_read(self, user_id: UUID) -> int:
        return Notification.objects.filter(recipient_id=user_id, is_read=False).update(is_read=True)
