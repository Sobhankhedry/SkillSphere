from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.notification import NotificationEntity


class NotificationRepository(ABC):
    @abstractmethod
    def create(self, entity: NotificationEntity) -> NotificationEntity: ...

    @abstractmethod
    def get_by_recipient(
        self, recipient_id: UUID, unread_only: bool = False
    ) -> list[NotificationEntity]: ...

    @abstractmethod
    def get_unread_count(self, recipient_id: UUID) -> int: ...

    @abstractmethod
    def mark_as_read(self, notification_id: UUID, user_id: UUID) -> bool: ...

    @abstractmethod
    def mark_all_read(self, user_id: UUID) -> int: ...
