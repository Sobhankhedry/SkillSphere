import uuid

from django.conf import settings
from django.db import models

from domain.enums import ActivityType


class ActivityLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
    )
    activity_type = models.CharField(
        max_length=20, choices=ActivityType.choices, db_index=True
    )
    description = models.TextField(blank=True, default="")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "activity_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "activity_type"], name="idx_actlog_user_type"),
            models.Index(fields=["-created_at"], name="idx_actlog_created"),
        ]

    def __str__(self):
        return f"{self.activity_type} by {self.user} at {self.created_at}"
