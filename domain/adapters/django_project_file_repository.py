from uuid import UUID

from apps.projects.models import ProjectFile
from domain.entities.project import ProjectFileEntity
from domain.ports.project_repository import ProjectFileRepository


def _to_entity(pf: ProjectFile) -> ProjectFileEntity:
    return ProjectFileEntity(
        id=pf.id,
        project_id=pf.project_id,
        original_filename=pf.original_filename,
        file_type=pf.file_type,
        file_size=pf.file_size,
        uploaded_by_id=pf.uploaded_by_id,
    )


class DjangoProjectFileRepository(ProjectFileRepository):
    def get_by_project(self, project_id: UUID) -> list[ProjectFileEntity]:
        return [
            _to_entity(f)
            for f in ProjectFile.objects.filter(project_id=project_id)
        ]

    def create(self, entity: ProjectFileEntity) -> ProjectFileEntity:
        return entity

    def delete(self, file_id: UUID) -> None:
        ProjectFile.objects.filter(id=file_id).delete()
