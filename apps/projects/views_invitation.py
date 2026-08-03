from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Invitation, Project
from .serializers_invitation import InvitationCreateSerializer, InvitationSerializer
from .services_invitation import InvitationService

User = get_user_model()


class InvitationViewSet(viewsets.ModelViewSet):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        return InvitationService.get_user_invitations(self.request.user)

    def destroy(self, request, *args, **kwargs):
        invitation = self.get_object()
        if invitation.inviter != request.user:
            return Response(
                {"error": "You can only cancel invitations you sent"},
                status=status.HTTP_403_FORBIDDEN,
            )
        invitation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        try:
            return Response({"message": "Invitation accepted"})
        except Invitation.DoesNotExist:
            return Response(
                {"error": "Invitation not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        try:
            return Response({"message": "Invitation declined"})
        except Invitation.DoesNotExist:
            return Response(
                {"error": "Invitation not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def pending(self, request):
        invitations = InvitationService.get_user_invitations(
            request.user, status="pending"
        )
        serializer = self.get_serializer(invitations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def sent(self, request):
        invitations = Invitation.objects.filter(inviter=request.user).select_related(
            "project", "invitee"
        )
        serializer = self.get_serializer(invitations, many=True)
        return Response(serializer.data)


class SendInvitationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(
                {"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = InvitationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            invitee = User.objects.get(
                username=serializer.validated_data["invitee_username"]
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            invitation = InvitationService.send_invitation(
                project=project,
                inviter=request.user,
                invitee=invitee,
                message=serializer.validated_data.get("message", ""),
            )
            return Response(
                InvitationSerializer(invitation).data,
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
