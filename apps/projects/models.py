import uuid

from django.conf import settings
from django.db import models

from domain.enums import FileType, InvitationStatus, ProjectStatus, ProjectVisibility


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, db_index=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tags"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="projects")
    visibility = models.CharField(
        max_length=10,
        choices=ProjectVisibility.choices,
        default=ProjectVisibility.PUBLIC,
    )
    status = models.CharField(
        max_length=10,
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT,
    )
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"], name="idx_project_owner_status"),
            models.Index(
                fields=["visibility", "status"], name="idx_project_vis_status"
            ),
            models.Index(fields=["-created_at"], name="idx_project_created"),
            models.Index(fields=["title"], name="idx_project_title"),
        ]

    def __str__(self):
        return self.title


def validate_file_size(value):
    max_size = 50 * 1024 * 1024  # 50MB
    if value.size > max_size:
        raise models.ValidationError(
            f"File size must be under {max_size // (1024*1024)}MB"
        )


def project_file_path(instance, filename):
    return f"projects/{instance.project.id}/files/{filename}"


class ProjectFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(
        upload_to=project_file_path, validators=[validate_file_size]
    )
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FileType.choices)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project_files"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project"], name="idx_projectfile_project"),
            models.Index(fields=["file_type"], name="idx_projectfile_type"),
        ]

    def __str__(self):
        return self.original_filename


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "-created_at"], name="idx_comment_project"),
            models.Index(fields=["author"], name="idx_comment_author"),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.project.title}"


class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="invitations"
    )
    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
    )
    invitee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="received_invitations",
    )
    message = models.TextField(max_length=500, blank=True, default="")
    status = models.CharField(
        max_length=15,
        choices=InvitationStatus.choices,
        default=InvitationStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "invitations"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["invitee", "status"], name="idx_invitation_invitee_status"
            ),
            models.Index(fields=["project"], name="idx_invitation_project"),
        ]
        unique_together = ["project", "invitee"]

    def __str__(self):
        return f"Invitation from {self.inviter.username} to {self.invitee.username} for {self.project.title}"
