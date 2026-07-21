import logging

from .documents import ProjectDocument, TagDocument, UserDocument, create_indices

logger = logging.getLogger(__name__)


def index_project(project):
    doc = ProjectDocument(
        id=str(project.id),
        title=project.title,
        description=project.description,
        owner_username=project.owner.username,
        tags=[
            {"name": t.name, "slug": t.slug} for t in project.tags.all()
        ],
        visibility=project.visibility,
        status=project.status,
        download_count=project.download_count,
        created_at=project.created_at,
    )
    doc.save()


def index_user(user):
    full_name = f"{user.first_name} {user.last_name}".strip()
    doc = UserDocument(
        id=str(user.id),
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=full_name,
    )
    doc.save()


def index_tag(tag):
    doc = TagDocument(
        id=str(tag.id),
        name=tag.name,
        slug=tag.slug,
    )
    doc.save()


def delete_project(project_id):
    try:
        ProjectDocument.get(id=str(project_id)).delete()
    except Exception:
        pass


def delete_user(user_id):
    try:
        UserDocument.get(id=str(user_id)).delete()
    except Exception:
        pass


def delete_tag(tag_id):
    try:
        TagDocument.get(id=str(tag_id)).delete()
    except Exception:
        pass


def bulk_index_all():
    from apps.projects.models import Project, Tag
    from apps.users.models import User

    create_indices()

    # Index projects
    projects = Project.objects.select_related("owner").prefetch_related("tags").all()
    for project in projects:
        try:
            index_project(project)
        except Exception as e:
            logger.error("Failed to index project %s: %s", project.id, e)
    logger.info("Indexed %d projects", projects.count())

    # Index users
    users = User.objects.all()
    for user in users:
        try:
            index_user(user)
        except Exception as e:
            logger.error("Failed to index user %s: %s", user.id, e)
    logger.info("Indexed %d users", users.count())

    # Index tags
    tags = Tag.objects.all()
    for tag in tags:
        try:
            index_tag(tag)
        except Exception as e:
            logger.error("Failed to index tag %s: %s", tag.id, e)
    logger.info("Indexed %d tags", tags.count())
