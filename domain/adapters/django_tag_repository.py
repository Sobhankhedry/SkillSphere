from apps.projects.models import Tag
from domain.entities.project import TagEntity
from domain.ports.project_repository import TagRepository


def _to_entity(tag: Tag) -> TagEntity:
    return TagEntity(id=tag.id, name=tag.name, slug=tag.slug)


class DjangoTagRepository(TagRepository):
    def get_or_create(self, names: list[str]) -> list[TagEntity]:
        tags = []
        for name in names:
            slug = name.lower().replace(" ", "-")
            tag, _ = Tag.objects.get_or_create(
                name=name.lower(), defaults={"slug": slug}
            )
            tags.append(_to_entity(tag))
        return tags

    def get_all(self) -> list[TagEntity]:
        return [_to_entity(t) for t in Tag.objects.all()]
