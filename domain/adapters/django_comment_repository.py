from uuid import UUID

from apps.projects.models import Comment
from domain.entities.project import CommentEntity
from domain.ports.project_repository import CommentRepository


def _to_entity(comment: Comment) -> CommentEntity:
    return CommentEntity(
        id=comment.id,
        project_id=comment.project_id,
        author_id=comment.author_id,
        content=comment.content,
    )


class DjangoCommentRepository(CommentRepository):
    def get_by_project(self, project_id: UUID) -> list[CommentEntity]:
        return [
            _to_entity(c)
            for c in Comment.objects.filter(project_id=project_id).order_by(
                "-created_at"
            )
        ]

    def create(self, entity: CommentEntity) -> CommentEntity:
        comment = Comment.objects.create(
            project_id=entity.project_id,
            author_id=entity.author_id,
            content=entity.content,
        )
        return _to_entity(comment)

    def update(self, entity: CommentEntity) -> CommentEntity:
        Comment.objects.filter(id=entity.id).update(content=entity.content)
        return entity

    def delete(self, comment_id: UUID) -> None:
        Comment.objects.filter(id=comment_id).delete()
