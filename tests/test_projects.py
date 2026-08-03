import pytest
from rest_framework import status

from apps.projects.models import Comment, Project
from apps.projects.services import CommentService, ProjectService


@pytest.mark.django_db
class TestProjectService:
    def test_create_project(self, user, tag):
        project = ProjectService.create_project(
            owner=user,
            data={
                "title": "My Project",
                "description": "Desc",
                "visibility": "public",
                "status": "draft",
            },
            tag_names=["python"],
        )
        assert project.title == "My Project"
        assert project.tags.count() == 1

    def test_update_project(self, project):
        updated = ProjectService.update_project(project, {"title": "Updated Title"})
        assert updated.title == "Updated Title"

    def test_get_visible_projects_public(self, user):
        ProjectService.create_project(
            owner=user,
            data={
                "title": "Public",
                "description": "d",
                "visibility": "public",
                "status": "published",
            },
        )
        projects = ProjectService.get_visible_projects()
        assert projects.count() == 1

    def test_get_visible_projects_private_hidden(self, user):
        ProjectService.create_project(
            owner=user,
            data={
                "title": "Private",
                "description": "d",
                "visibility": "private",
                "status": "published",
            },
        )
        projects = ProjectService.get_visible_projects()
        assert projects.count() == 0

    def test_delete_project(self, project):
        project_id = project.id
        ProjectService.delete_project(project)
        assert not Project.objects.filter(id=project_id).exists()


@pytest.mark.django_db
class TestCommentService:
    def test_create_comment(self, project, user):
        comment = CommentService.create_comment(project, user, "Great project!")
        assert comment.content == "Great project!"
        assert comment.author == user

    def test_update_comment(self, project, user):
        comment = CommentService.create_comment(project, user, "Original")
        updated = CommentService.update_comment(comment, "Updated")
        assert updated.content == "Updated"

    def test_delete_comment(self, project, user):
        comment = CommentService.create_comment(project, user, "Delete me")
        comment_id = comment.id
        CommentService.delete_comment(comment)
        assert not Comment.objects.filter(id=comment_id).exists()


@pytest.mark.django_db
class TestProjectAPI:
    def test_list_projects(self, authenticated_client, project):
        response = authenticated_client.get("/api/v1/projects/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_project(self, authenticated_client):
        response = authenticated_client.post(
            "/api/v1/projects/",
            {
                "title": "New Project",
                "description": "Description here",
                "visibility": "public",
                "status": "draft",
                "tag_names": ["django", "python"],
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Project"

    def test_get_project(self, authenticated_client, project):
        response = authenticated_client.get(f"/api/v1/projects/{project.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Test Project"

    def test_update_project(self, authenticated_client, project):
        response = authenticated_client.patch(
            f"/api/v1/projects/{project.id}/",
            {"title": "Updated Project"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_delete_project(self, authenticated_client, project):
        response = authenticated_client.delete(f"/api/v1/projects/{project.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_cannot_update_others_project(self, authenticated_client, admin_user):
        other_project = Project.objects.create(
            title="Admin Project",
            description="d",
            owner=admin_user,
        )
        response = authenticated_client.patch(
            f"/api/v1/projects/{other_project.id}/",
            {"title": "Hacked"},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_my_projects(self, authenticated_client, project):
        response = authenticated_client.get("/api/v1/projects/my_projects/")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCommentAPI:
    def test_list_comments(self, authenticated_client, project, user):
        CommentService.create_comment(project, user, "Comment 1")
        response = authenticated_client.get(f"/api/v1/comments/?project={project.id}")
        assert response.status_code == status.HTTP_200_OK

    def test_create_comment(self, authenticated_client, project):
        response = authenticated_client.post(
            "/api/v1/comments/",
            {"project": str(project.id), "content": "Nice work!"},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_delete_own_comment(self, authenticated_client, project, user):
        comment = CommentService.create_comment(project, user, "Delete me")
        response = authenticated_client.delete(f"/api/v1/comments/{comment.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
