from rest_framework import serializers

from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True, default=None)

    class Meta:
        model = ActivityLog
        fields = [
            "id", "username", "activity_type", "description",
            "ip_address", "metadata", "created_at",
        ]
        read_only_fields = fields
