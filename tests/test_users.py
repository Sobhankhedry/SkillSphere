import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.users.models import Profile
from apps.users.services import UserService

User = get_user_model()


@pytest.mark.django_db
class TestUserService:
    def test_register_user(self):
        user = UserService.register_user(
            email="new@example.com",
            username="newuser",
            password="pass12345",
            first_name="New",
            last_name="User",
        )
        assert user.email == "new@example.com"
        assert user.username == "newuser"
        assert Profile.objects.filter(user=user).exists()

    def test_register_duplicate_email(self):
        UserService.register_user("dup@example.com", "user1", "pass12345")
        with pytest.raises(Exception):
            UserService.register_user("dup@example.com", "user2", "pass12345")

    def test_register_duplicate_username(self):
        UserService.register_user("a@example.com", "dupuser", "pass12345")
        with pytest.raises(Exception):
            UserService.register_user("b@example.com", "dupuser", "pass12345")

    def test_update_profile(self):
        user = UserService.register_user("prof@example.com", "profuser", "pass12345")
        profile = UserService.update_profile(user, bio="Hello world")
        assert profile.bio == "Hello world"

    def test_get_user_by_email(self):
        user = UserService.register_user("find@example.com", "finduser", "pass12345")
        found = UserService.get_user_by_email("find@example.com")
        assert found.id == user.id

    def test_get_user_by_username(self):
        user = UserService.register_user("byuname@example.com", "byuname", "pass12345")
        found = UserService.get_user_by_username("byuname")
        assert found.id == user.id


@pytest.mark.django_db
class TestRegisterAPI:
    def test_register_success(self, api_client):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "api@example.com",
                "username": "apiuser",
                "password": "pass12345",
                "password_confirm": "pass12345",
                "first_name": "Api",
                "last_name": "User",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="api@example.com").exists()

    def test_register_password_mismatch(self, api_client):
        response = api_client.post(
            "/api/v1/auth/register/",
            {
                "email": "mismatch@example.com",
                "username": "mismatch",
                "password": "pass12345",
                "password_confirm": "different",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginAPI:
    def test_login_success(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": "test@example.com", "password": "testpass123"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_invalid_credentials(self, api_client, user):
        response = api_client.post(
            "/api/v1/auth/login/",
            {"email": "test@example.com", "password": "wrongpass"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProfileAPI:
    def test_get_profile(self, authenticated_client, user):
        response = authenticated_client.get("/api/v1/users/profiles/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"]["email"] == "test@example.com"

    def test_update_profile(self, authenticated_client, user):
        response = authenticated_client.patch(
            "/api/v1/users/profiles/me/",
            {"bio": "Updated bio"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["bio"] == "Updated bio"

    def test_unauthenticated_profile(self, api_client):
        response = api_client.get("/api/v1/users/profiles/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
