from rest_framework import serializers

from .models import Feedback, Notification


class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(
        source="sender.username", read_only=True, default=None
    )

    class Meta:
        model = Notification
        fields = [
            "id", "sender", "sender_username", "notification_type",
            "title", "message", "link", "is_read", "created_at",
        ]
        read_only_fields = [
            "id", "sender", "sender_username", "notification_type",
            "title", "message", "link", "is_read", "created_at",
        ]


class NotificationMarkReadSerializer(serializers.Serializer):
    notification_id = serializers.UUIDField()


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            "id", "severity", "title", "message", "action",
            "is_read", "created_at",
        ]
        read_only_fields = [
            "id", "severity", "title", "message", "action", "created_at",
        ]
