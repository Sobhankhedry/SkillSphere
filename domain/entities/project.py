from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class TagEntity:
    id: UUID
    name: str
    slug: str


@dataclass
class ProjectEntity:
    id: UUID
    title: str
    description: str
    owner_id: UUID
    visibility: str = "public"
    status: str = "draft"
    download_count: int = 0
    tags: list[TagEntity] = field(default_factory=list)

    def is_visible_to(self, user_id: UUID | None) -> bool:
        if self.visibility == "public":
            return True
        return user_id == self.owner_id


@dataclass
class ProjectFileEntity:
    id: UUID
    project_id: UUID
    original_filename: str
    file_type: str
    file_size: int
    uploaded_by_id: UUID


@dataclass
class CommentEntity:
    id: UUID
    project_id: UUID
    author_id: UUID
    content: str
