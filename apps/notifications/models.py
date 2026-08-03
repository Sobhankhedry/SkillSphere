import uuid

from django.conf import settings
from django.db import models

from domain.enums import NotificationType


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_notifications",
    )
    notification_type = models.CharField(
        max_length=20, choices=NotificationType.choices
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, default="")
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["recipient", "is_read", "-created_at"],
                name="idx_notif_recipient_read",
            ),
            models.Index(fields=["notification_type"], name="idx_notif_type"),
        ]

    def __str__(self):
        return f"{self.notification_type} to {self.recipient.username}"

    def mark_read(self):
        self.is_read = True
        self.save(update_fields=["is_read"])


class Feedback(models.Model):
    class Severity(models.TextChoices):
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"
        WARNING = "warning", "Warning"
        INFO = "info", "Info"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedbacks",
    )
    severity = models.CharField(max_length=10, choices=Severity.choices)
    title = models.CharField(max_length=255)
    message = models.TextField()
    action = models.CharField(max_length=100, blank=True, default="")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "feedbacks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "is_read", "-created_at"],
                name="idx_feedback_user_read",
            ),
        ]

    def __str__(self):
        return f"[{self.severity}] {self.title} to {self.user.username}"

    def mark_read(self):
        self.is_read = True
        self.save(update_fields=["is_read"])
