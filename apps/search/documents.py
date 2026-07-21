from elasticsearch import exceptions as es_exceptions
from elasticsearch_dsl import (
    Document,
    Date,
    Keyword,
    Nested,
    Short,
    Text,
)

from .es_client import get_es_client


class ProjectDocument(Document):
    id = Keyword()
    title = Text(analyzer="english", fields={"raw": Keyword()})
    description = Text(analyzer="english")
    owner_username = Text(fields={"raw": Keyword()})
    tags = Nested(
        properties={
            "name": Text(analyzer="english", fields={"raw": Keyword()}),
            "slug": Keyword(),
        }
    )
    visibility = Keyword()
    status = Keyword()
    download_count = Short()
    created_at = Date()

    class Index:
        name = "projects"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }


class UserDocument(Document):
    id = Keyword()
    username = Text(fields={"raw": Keyword()})
    email = Keyword()
    first_name = Text()
    last_name = Text()
    full_name = Text()

    class Index:
        name = "users"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }


class TagDocument(Document):
    id = Keyword()
    name = Text(analyzer="english", fields={"raw": Keyword()})
    slug = Keyword()

    class Index:
        name = "tags"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }


def create_indices():
    get_es_client()
    for doc_cls in [ProjectDocument, UserDocument, TagDocument]:
        try:
            doc_cls._index.delete()
        except es_exceptions.NotFoundError:
            pass
        doc_cls._index.create()
