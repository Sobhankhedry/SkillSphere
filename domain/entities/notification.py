from dataclasses import dataclass
from uuid import UUID


@dataclass
class NotificationEntity:
    id: UUID
    recipient_id: UUID
    notification_type: str
    title: str
    message: str
    sender_id: UUID | None = None
    link: str = ""
    is_read: bool = False
