from uuid import UUID

from django.contrib.auth import get_user_model

from apps.users.models import Profile
from domain.entities.user import ProfileEntity, UserEntity
from domain.ports.user_repository import UserRepository

User = get_user_model()


def _to_entity(user: User) -> UserEntity:
    return UserEntity(
        id=user.id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        email_verified=user.email_verified,
    )


def _profile_to_entity(profile: Profile) -> ProfileEntity:
    return ProfileEntity(
        id=profile.id,
        user_id=profile.user_id,
        bio=profile.bio,
        avatar=profile.avatar.url if profile.avatar else None,
        github_link=profile.github_link,
        linkedin_link=profile.linkedin_link,
    )


class DjangoUserRepository(UserRepository):
    def get_by_id(self, user_id: UUID) -> UserEntity | None:
        try:
            return _to_entity(User.objects.get(id=user_id))
        except User.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> UserEntity | None:
        try:
            return _to_entity(User.objects.get(email=email))
        except User.DoesNotExist:
            return None

    def get_by_username(self, username: str) -> UserEntity | None:
        try:
            return _to_entity(
                User.objects.select_related("profile").get(username=username)
            )
        except User.DoesNotExist:
            return None

    def create(self, email: str, username: str, password: str, **kwargs) -> UserEntity:
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            **kwargs,
        )
        Profile.objects.get_or_create(user=user)
        return _to_entity(user)

    def update(self, user_id: UUID, **kwargs) -> UserEntity:
        User.objects.filter(id=user_id).update(**kwargs)
        return _to_entity(User.objects.get(id=user_id))

    def get_profile(self, user_id: UUID) -> ProfileEntity | None:
        try:
            profile = Profile.objects.get(user_id=user_id)
            return _profile_to_entity(profile)
        except Profile.DoesNotExist:
            return None

    def update_profile(self, user_id: UUID, **kwargs) -> ProfileEntity:
        profile, _ = Profile.objects.get_or_create(user_id=user_id)
        for field, value in kwargs.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        profile.save()
        return _profile_to_entity(profile)
