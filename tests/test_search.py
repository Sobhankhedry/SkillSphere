import pytest
from rest_framework import status

from apps.projects.services import ProjectService
from apps.search.services import SearchService


def _es_available():
    try:
        from apps.search.es_client import get_es_client
        get_es_client()
        return True
    except Exception:
        return False


@pytest.mark.django_db
class TestSearchService:
    @pytest.mark.xfail(reason="ES index may be stale/empty in test environment", strict=False)
    def test_search_projects(self, user):
        ProjectService.create_project(
            owner=user,
            data={
                "title": "Django REST API",
                "description": "Building a REST API",
                "visibility": "public",
                "status": "published",
            },
        )
        results = SearchService.search_projects("Django")
        assert len(results) == 1

    @pytest.mark.xfail(reason="ES index may have stale data from prior runs", strict=False)
    def test_search_users(self, user):
        results = SearchService.search_users("testuser")
        assert len(results) == 1

    @pytest.mark.xfail(reason="ES index may have stale data from prior runs", strict=False)
    def test_global_search(self, user):
        ProjectService.create_project(
            owner=user,
            data={
                "title": "Python ML Project",
                "description": "Machine learning with Python",
                "visibility": "public",
                "status": "published",
            },
        )
        results = SearchService.global_search("Python")
        assert len(results["projects"]) == 1


@pytest.mark.django_db
class TestSearchAPI:
    def test_global_search(self, authenticated_client, user):
        response = authenticated_client.get("/api/v1/search/?q=Searchable")
        assert response.status_code == status.HTTP_200_OK
        assert "projects" in response.data

    def test_empty_search(self, authenticated_client):
        response = authenticated_client.get("/api/v1/search/?q=")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.skipif(not _es_available(), reason="Elasticsearch not available")
    def test_project_search(self, authenticated_client, user):
        ProjectService.create_project(
            owner=user,
            data={
                "title": "Elastic Search Demo",
                "description": "d",
                "visibility": "public",
                "status": "published",
            },
        )
        response = authenticated_client.get("/api/v1/search/projects/?q=Elastic")
        assert response.status_code == status.HTTP_200_OK
