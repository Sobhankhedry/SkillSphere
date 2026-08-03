from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.project import (
    CommentEntity,
    ProjectEntity,
    ProjectFileEntity,
    TagEntity,
)


class ProjectRepository(ABC):
    @abstractmethod
    def get_by_id(self, project_id: UUID) -> ProjectEntity | None: ...

    @abstractmethod
    def get_visible_to(self, user_id: UUID | None) -> list[ProjectEntity]: ...

    @abstractmethod
    def get_by_owner(self, owner_id: UUID) -> list[ProjectEntity]: ...

    @abstractmethod
    def create(self, entity: ProjectEntity) -> ProjectEntity: ...

    @abstractmethod
    def update(self, entity: ProjectEntity) -> ProjectEntity: ...

    @abstractmethod
    def delete(self, project_id: UUID) -> None: ...

    @abstractmethod
    def increment_download(self, project_id: UUID) -> None: ...


class TagRepository(ABC):
    @abstractmethod
    def get_or_create(self, names: list[str]) -> list[TagEntity]: ...

    @abstractmethod
    def get_all(self) -> list[TagEntity]: ...


class CommentRepository(ABC):
    @abstractmethod
    def get_by_project(self, project_id: UUID) -> list[CommentEntity]: ...

    @abstractmethod
    def create(self, entity: CommentEntity) -> CommentEntity: ...

    @abstractmethod
    def update(self, entity: CommentEntity) -> CommentEntity: ...

    @abstractmethod
    def delete(self, comment_id: UUID) -> None: ...


class ProjectFileRepository(ABC):
    @abstractmethod
    def get_by_project(self, project_id: UUID) -> list[ProjectFileEntity]: ...

    @abstractmethod
    def create(self, entity: ProjectFileEntity) -> ProjectFileEntity: ...

    @abstractmethod
    def delete(self, file_id: UUID) -> None: ...
