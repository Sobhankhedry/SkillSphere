from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.db.models import Q, QuerySet

from .models import Comment, Project, ProjectFile, Tag

User = get_user_model()


class TagService:
    @staticmethod
    def get_or_create_tags(tag_names: list[str]) -> list[Tag]:
        tags = []
        for name in tag_names:
            slug = name.lower().replace(" ", "-")
            tag, _ = Tag.objects.get_or_create(
                name=name.lower(), defaults={"slug": slug}
            )
            tags.append(tag)
        return tags


class ProjectService:
    @staticmethod
    def create_project(owner: User, data: dict, tag_names: list[str] = None) -> Project:
        with transaction.atomic():
            project = Project.objects.create(
                title=data["title"],
                description=data["description"],
                owner=owner,
                visibility=data.get("visibility", "public"),
                status=data.get("status", "draft"),
            )
            if tag_names:
                tags = TagService.get_or_create_tags(tag_names)
                project.tags.set(tags)
            return project

    @staticmethod
    def update_project(
        project: Project, data: dict, tag_names: list[str] = None
    ) -> Project:
        with transaction.atomic():
            for field, value in data.items():
                if hasattr(project, field) and field not in ("owner", "id"):
                    setattr(project, field, value)
            project.full_clean()
            project.save()
            if tag_names is not None:
                tags = TagService.get_or_create_tags(tag_names)
                project.tags.set(tags)
            return project

    @staticmethod
    def get_visible_projects(user: User | None = None) -> QuerySet:
        queryset = Project.objects.select_related("owner").prefetch_related("tags")
        if user and user.is_authenticated:
            return queryset.filter(Q(visibility="public") | Q(owner=user))
        return queryset.filter(visibility="public")

    @staticmethod
    def get_user_projects(user: User) -> QuerySet:
        return (
            Project.objects.filter(owner=user)
            .select_related("owner")
            .prefetch_related("tags")
        )

    @staticmethod
    def delete_project(project: Project) -> None:
        project.delete()

    @staticmethod
    def increment_download(project: Project) -> None:
        Project.objects.filter(pk=project.pk).update(
            download_count=models.F("download_count") + 1
        )


class FileService:
    @staticmethod
    @transaction.atomic
    def upload_file(
        project: Project, file_obj, user: User, filename: str, file_type: str
    ) -> ProjectFile:
        file_size = file_obj.size
        project_file = ProjectFile.objects.create(
            project=project,
            file=file_obj,
            original_filename=filename,
            file_type=file_type,
            file_size=file_size,
            uploaded_by=user,
        )
        return project_file

    @staticmethod
    def get_project_files(project: Project) -> QuerySet:
        return ProjectFile.objects.filter(project=project)

    @staticmethod
    def delete_file(project_file: ProjectFile) -> None:
        project_file.file.delete(save=False)
        project_file.delete()


class CommentService:
    @staticmethod
    def create_comment(project: Project, author: User, content: str) -> Comment:
        comment = Comment.objects.create(
            project=project, author=author, content=content
        )
        if project.owner != author:
            from apps.notifications.services import NotificationService

            NotificationService.create_notification(
                recipient=project.owner,
                notification_type="new_comment",
                title="New comment on your project",
                message=f"{author.username} commented on '{project.title}': {content[:200]}",
                sender=author,
                link=f"/projects/{project.id}",
            )
        return comment

    @staticmethod
    def update_comment(comment: Comment, content: str) -> Comment:
        comment.content = content
        comment.full_clean()
        comment.save()
        return comment

    @staticmethod
    def delete_comment(comment: Comment) -> None:
        comment.delete()

    @staticmethod
    def get_project_comments(project: Project) -> QuerySet:
        return (
            Comment.objects.filter(project=project)
            .select_related("author")
            .order_by("-created_at")
        )
