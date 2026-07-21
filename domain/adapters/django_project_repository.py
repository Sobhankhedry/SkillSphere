from uuid import UUID

from django.db import models
from django.db.models import Q

from apps.projects.models import Project
from domain.entities.project import ProjectEntity
from domain.ports.project_repository import ProjectRepository


def _to_entity(project: Project) -> ProjectEntity:
    return ProjectEntity(
        id=project.id,
        title=project.title,
        description=project.description,
        owner_id=project.owner_id,
        visibility=project.visibility,
        status=project.status,
        download_count=project.download_count,
    )


class DjangoProjectRepository(ProjectRepository):
    def get_by_id(self, project_id: UUID) -> ProjectEntity | None:
        try:
            project = Project.objects.get(id=project_id)
            return _to_entity(project)
        except Project.DoesNotExist:
            return None

    def get_visible_to(self, user_id: UUID | None) -> list[ProjectEntity]:
        qs = Project.objects.filter(visibility="public")
        if user_id:
            qs = qs | Project.objects.filter(owner_id=user_id)
        return [_to_entity(p) for p in qs.distinct()]

    def get_by_owner(self, owner_id: UUID) -> list[ProjectEntity]:
        return [_to_entity(p) for p in Project.objects.filter(owner_id=owner_id)]

    def create(self, entity: ProjectEntity) -> ProjectEntity:
        project = Project.objects.create(
            title=entity.title,
            description=entity.description,
            owner_id=entity.owner_id,
            visibility=entity.visibility,
            status=entity.status,
        )
        return _to_entity(project)

    def update(self, entity: ProjectEntity) -> ProjectEntity:
        Project.objects.filter(id=entity.id).update(
            title=entity.title,
            description=entity.description,
            visibility=entity.visibility,
            status=entity.status,
        )
        return self.get_by_id(entity.id)

    def delete(self, project_id: UUID) -> None:
        Project.objects.filter(id=project_id).delete()

    def increment_download(self, project_id: UUID) -> None:
        Project.objects.filter(id=project_id).update(
            download_count=models.F("download_count") + 1
        )
