import os

from django.db import models
from django.http import FileResponse, Http404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from domain.enums import FileType

from .models import Project, ProjectFile, Tag
from .serializers import (
    ProjectFileSerializer,
    ProjectSerializer,
    TagSerializer,
)
from .services import FileService, ProjectService


class IsOwnerOrCollaboratorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if obj.owner == request.user:
            return True
        from .models import Invitation
        from domain.enums import InvitationStatus

        return Invitation.objects.filter(
            project=obj, invitee=request.user, status=InvitationStatus.ACCEPTED
        ).exists()


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrCollaboratorOrReadOnly,
    ]

    def get_queryset(self):
        return ProjectService.get_visible_projects(self.request.user)

    def perform_create(self, serializer):
        tag_names = self.request.data.get("tag_names", [])
        if isinstance(tag_names, str):
            tag_names = [t.strip() for t in tag_names.split(",") if t.strip()]
        invite_usernames = serializer.validated_data.pop("invite_usernames", [])
        project = ProjectService.create_project(
            owner=self.request.user,
            data=serializer.validated_data,
            tag_names=tag_names,
        )
        serializer.instance = project

        if invite_usernames:
            from apps.projects.services_invitation import InvitationService
            from django.contrib.auth import get_user_model

            User = get_user_model()
            for username in invite_usernames:
                try:
                    invitee = User.objects.get(username=username)
                    InvitationService.send_invitation(
                        project=project,
                        inviter=self.request.user,
                        invitee=invitee,
                    )
                except User.DoesNotExist:
                    continue

        from apps.activity_logs.services import ActivityLogService
        from apps.notifications.services import FeedbackService

        ActivityLogService.log_activity(
            user=self.request.user,
            activity_type="project_created",
            description=f"Created project '{project.title}'",
        )
        FeedbackService.success(
            user=self.request.user,
            title="Project created",
            message=f"Your project '{project.title}' has been created successfully.",
        )

    def perform_update(self, serializer):
        tag_names = self.request.data.get("tag_names")
        if tag_names is not None:
            if isinstance(tag_names, str):
                tag_names = [t.strip() for t in tag_names.split(",") if t.strip()]
        ProjectService.update_project(
            project=serializer.instance,
            data=serializer.validated_data,
            tag_names=tag_names,
        )
        from apps.activity_logs.services import ActivityLogService

        ActivityLogService.log_activity(
            user=self.request.user,
            activity_type="project_updated",
            description=f"Updated project '{serializer.instance.title}'",
        )

    def perform_destroy(self, instance):
        title = instance.title
        ProjectService.delete_project(instance)
        from apps.activity_logs.services import ActivityLogService

        ActivityLogService.log_activity(
            user=self.request.user,
            activity_type="project_deleted",
            description=f"Deleted project '{title}'",
        )

    def get_parser_classes(self):
        if self.action == "upload_file":
            return [MultiPartParser, FormParser]
        return [JSONParser]

    @action(detail=True, methods=["get"])
    def files(self, request, pk=None):
        project = self.get_object()
        files = FileService.get_project_files(project)
        serializer = ProjectFileSerializer(files, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
    )
    def upload_file(self, request, pk=None):
        project = self.get_object()
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response(
                {"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        ext = os.path.splitext(file_obj.name)[1].lower()
        file_type_map = {
            ".pdf": FileType.PDF,
            ".zip": FileType.ZIP,
            ".jpg": FileType.IMAGE,
            ".jpeg": FileType.IMAGE,
            ".png": FileType.IMAGE,
            ".gif": FileType.IMAGE,
            ".webp": FileType.IMAGE,
        }
        file_type = file_type_map.get(ext)
        if not file_type:
            return Response(
                {"error": f"File type {ext} is not allowed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project_file = FileService.upload_file(
            project=project,
            file_obj=file_obj,
            user=request.user,
            filename=file_obj.name,
            file_type=file_type.value,
        )
        from apps.activity_logs.services import ActivityLogService
        from apps.notifications.services import FeedbackService

        ActivityLogService.log_activity(
            user=request.user,
            activity_type="file_uploaded",
            description=f"Uploaded file '{file_obj.name}' to project '{project.title}'",
            metadata={"file_id": str(project_file.id), "file_type": file_type.value},
        )
        FeedbackService.success(
            user=request.user,
            title="File uploaded",
            message=f"File '{file_obj.name}' has been uploaded to '{project.title}' successfully.",
        )
        return Response(
            ProjectFileSerializer(project_file).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="download/(?P<file_id>[^/.]+)")
    def download_file(self, request, pk=None, file_id=None):
        project = self.get_object()
        try:
            project_file = ProjectFile.objects.get(id=file_id, project=project)
        except ProjectFile.DoesNotExist:
            raise Http404

        response = FileResponse(project_file.file.open("rb"))
        response["Content-Disposition"] = (
            f'attachment; filename="{project_file.original_filename}"'
        )
        Project.objects.filter(pk=project.pk).update(
            download_count=models.F("download_count") + 1
        )
        from apps.activity_logs.services import ActivityLogService

        ActivityLogService.log_activity(
            user=request.user,
            activity_type="file_downloaded",
            description=f"Downloaded file '{project_file.original_filename}' from project '{project.title}'",
            metadata={"file_id": str(project_file.id)},
        )
        return response

    @action(detail=True, methods=["get"])
    def collaborators(self, request, pk=None):
        project = self.get_object()
        from .models import Invitation

        invitations = Invitation.objects.filter(project=project).select_related(
            "invitee"
        )
        data = []
        for inv in invitations:
            data.append(
                {
                    "id": str(inv.id),
                    "username": inv.invitee.username,
                    "status": inv.status,
                    "created_at": inv.created_at.isoformat(),
                }
            )
        return Response(data)

    @action(detail=False, methods=["get"])
    def my_projects(self, request):
        projects = ProjectService.get_user_projects(request.user)
        page = self.paginate_queryset(projects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def collaborating(self, request):
        from .models import Invitation
        from domain.enums import InvitationStatus

        project_ids = Invitation.objects.filter(
            invitee=request.user, status=InvitationStatus.ACCEPTED
        ).values_list("project_id", flat=True)
        projects = (
            Project.objects.filter(id__in=project_ids)
            .select_related("owner")
            .prefetch_related("tags")
        )
        page = self.paginate_queryset(projects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
