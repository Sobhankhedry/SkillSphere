from rest_framework import permissions, viewsets

from .models import Comment, Project
from .serializers import CommentSerializer
from .services import CommentService


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.select_related("author", "project")
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def perform_create(self, serializer):
        project_id = self.request.data.get("project")
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            from rest_framework.exceptions import NotFound

            raise NotFound("Project not found")

        comment = CommentService.create_comment(
            project=project,
            author=self.request.user,
            content=serializer.validated_data["content"],
        )
        serializer.instance = comment
        from apps.activity_logs.services import ActivityLogService

        ActivityLogService.log_activity(
            user=self.request.user,
            activity_type="comment_created",
            description=f"Commented on project '{project.title}'",
            metadata={"project_id": str(project.id), "comment_id": str(comment.id)},
        )

    def perform_update(self, serializer):
        CommentService.update_comment(
            comment=serializer.instance,
            content=serializer.validated_data.get(
                "content", serializer.instance.content
            ),
        )

    def perform_destroy(self, instance):
        CommentService.delete_comment(instance)
