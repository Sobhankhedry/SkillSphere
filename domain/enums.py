from django.db.models import TextChoices


class UserRole(TextChoices):
    USER = "user", "User"
    ADMIN = "admin", "Admin"


class ProjectStatus(TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"


class ProjectVisibility(TextChoices):
    PUBLIC = "public", "Public"
    PRIVATE = "private", "Private"


class NotificationType(TextChoices):
    NEW_COMMENT = "new_comment", "New Comment"
    INVITATION = "invitation", "Invitation"
    SYSTEM_MESSAGE = "system_message", "System Message"


class ActivityType(TextChoices):
    LOGIN = "login", "Login"
    LOGOUT = "logout", "Logout"
    PROJECT_CREATED = "project_created", "Project Created"
    PROJECT_UPDATED = "project_updated", "Project Updated"
    PROJECT_DELETED = "project_deleted", "Project Deleted"
    FILE_UPLOADED = "file_uploaded", "File Uploaded"
    FILE_DOWNLOADED = "file_downloaded", "File Downloaded"
    COMMENT_CREATED = "comment_created", "Comment Created"
    API_REQUEST = "api_request", "API Request"


class FileType(TextChoices):
    PDF = "pdf", "PDF"
    ZIP = "zip", "ZIP"
    IMAGE = "image", "Image"


class InvitationStatus(TextChoices):
    PENDING = "pending", "Pending"
    ACCEPTED = "accepted", "Accepted"
    DECLINED = "declined", "Declined"
