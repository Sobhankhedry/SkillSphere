from elasticsearch_dsl import Q, Search

from .documents import ProjectDocument, TagDocument, UserDocument
from .es_client import get_es_client


def _es_search(doc_class, query, extra_filters=None, highlight_fields=None):
    get_es_client()
    s = Search(index=doc_class._index._name).query(
        Q(
            "multi_match",
            query=query,
            fields=["*"],
            fuzziness="AUTO",
        )
    )
    if extra_filters:
        for f in extra_filters:
            s = s.filter(f)
    if highlight_fields:
        s = s.highlight_options(pre_tags=["<mark>"], post_tags=["</mark>"])
        s = s.highlight(*highlight_fields)
    return s


class SearchService:
    @staticmethod
    def search_projects(query, user=None):
        filters = [Q("term", status="published")]
        if user and user.is_authenticated:
            # Public projects + user's own private projects
            filters = [
                Q("bool", should=[Q("term", visibility="public"), Q("term", owner_username=user.username)], minimum_should_match=1)
            ]
        s = _es_search(
            ProjectDocument,
            query,
            extra_filters=filters,
            highlight_fields=["title", "description"],
        )
        s = s.sort("-created_at")[:20]
        response = s.execute()
        return [
            {
                "id": hit.id,
                "title": hit.title,
                "description": getattr(hit, "description", ""),
                "owner_username": getattr(hit, "owner_username", ""),
                "tags": [{"name": t.name, "slug": t.slug} for t in getattr(hit, "tags", [])],
                "download_count": getattr(hit, "download_count", 0),
            }
            for hit in response
        ]

    @staticmethod
    def search_users(query):
        get_es_client()
        s = Search(index=UserDocument._index._name).query(
            Q(
                "multi_match",
                query=query,
                fields=["username", "first_name", "last_name", "email", "full_name"],
                fuzziness="AUTO",
            )
        )[:20]
        response = s.execute()
        return [
            {
                "id": hit.id,
                "username": hit.username,
                "first_name": getattr(hit, "first_name", ""),
                "last_name": getattr(hit, "last_name", ""),
            }
            for hit in response
        ]

    @staticmethod
    def search_tags(query):
        get_es_client()
        s = Search(index=TagDocument._index._name).query(
            Q("match", name={"query": query, "fuzziness": "AUTO"})
        )[:20]
        response = s.execute()
        return [
            {"id": hit.id, "name": hit.name, "slug": hit.slug}
            for hit in response
        ]

    @staticmethod
    def global_search(query, user=None):
        return {
            "projects": SearchService.search_projects(query, user),
            "users": SearchService.search_users(query),
            "tags": SearchService.search_tags(query),
        }
