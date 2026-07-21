from rest_framework import serializers

from .models import Invitation


class InvitationSerializer(serializers.ModelSerializer):
    inviter_username = serializers.CharField(
        source="inviter.username", read_only=True
    )
    invitee_username = serializers.CharField(
        source="invitee.username", read_only=True
    )
    project_title = serializers.CharField(source="project.title", read_only=True)

    class Meta:
        model = Invitation
        fields = [
            "id",
            "project",
            "project_title",
            "inviter",
            "inviter_username",
            "invitee",
            "invitee_username",
            "message",
            "status",
            "created_at",
            "responded_at",
        ]
        read_only_fields = [
            "id",
            "inviter",
            "inviter_username",
            "invitee_username",
            "project_title",
            "status",
            "created_at",
            "responded_at",
        ]


class InvitationCreateSerializer(serializers.Serializer):
    invitee_username = serializers.CharField()
    message = serializers.CharField(max_length=500, required=False, default="")
