from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.notifications.services import NotificationService
from domain.enums import InvitationStatus

from .models import Invitation, Project

User = get_user_model()


class InvitationService:
    @staticmethod
    @transaction.atomic
    def send_invitation(
        project: Project,
        inviter: User,
        invitee: User,
        message: str = "",
    ) -> Invitation:
        if project.owner != inviter:
            raise ValueError("Only the project owner can send invitations")
        if inviter == invitee:
            raise ValueError("Cannot invite yourself")

        invitation, created = Invitation.objects.get_or_create(
            project=project,
            invitee=invitee,
            defaults={"inviter": inviter, "message": message},
        )
        if not created:
            raise ValueError("Invitation already exists for this user on this project")

        NotificationService.create_notification(
            recipient=invitee,
            notification_type="invitation",
            title="Project collaboration invitation",
            message=f"{inviter.username} invited you to collaborate on '{project.title}'.{f' Message: {message}' if message else ''}",
            sender=inviter,
            link=f"/projects/{project.id}",
        )
        return invitation

    @staticmethod
    @transaction.atomic
    def accept_invitation(invitation_id: str, user: User) -> Invitation:
        invitation = Invitation.objects.get(id=invitation_id, invitee=user)
        if invitation.status != InvitationStatus.PENDING:
            raise ValueError("Invitation is no longer pending")
        invitation.status = InvitationStatus.ACCEPTED
        invitation.responded_at = timezone.now()
        invitation.save(update_fields=["status", "responded_at"])

        NotificationService.create_notification(
            recipient=invitation.inviter,
            notification_type="system_message",
            title="Invitation accepted",
            message=f"{user.username} accepted your invitation to collaborate on '{invitation.project.title}'.",
            sender=user,
            link=f"/projects/{invitation.project.id}",
        )
        return invitation

    @staticmethod
    @transaction.atomic
    def decline_invitation(invitation_id: str, user: User) -> Invitation:
        invitation = Invitation.objects.get(id=invitation_id, invitee=user)
        if invitation.status != InvitationStatus.PENDING:
            raise ValueError("Invitation is no longer pending")
        invitation.status = InvitationStatus.DECLINED
        invitation.responded_at = timezone.now()
        invitation.save(update_fields=["status", "responded_at"])
        return invitation

    @staticmethod
    def get_user_invitations(user: User, status: str = None):
        queryset = Invitation.objects.filter(invitee=user).select_related(
            "project", "inviter"
        )
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @staticmethod
    def get_project_invitations(project: Project):
        return Invitation.objects.filter(project=project).select_related("invitee")
