from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Profile

User = get_user_model()


class UserService:
    @staticmethod
    @transaction.atomic
    def register_user(
        email: str, username: str, password: str, first_name: str = "", last_name: str = ""
    ) -> User:
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already registered")
        if User.objects.filter(username=username).exists():
            raise ValidationError("Username already taken")

        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        Profile.objects.create(user=user)
        return user

    @staticmethod
    def get_user_by_email(email: str) -> User | None:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user_by_username(username: str) -> User | None:
        try:
            return User.objects.select_related("profile").get(username=username)
        except User.DoesNotExist:
            return None

    @staticmethod
    def update_profile(user: User, **data) -> Profile:
        profile, _ = Profile.objects.get_or_create(user=user)
        for field, value in data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        profile.full_clean()
        profile.save()
        return profile

    @staticmethod
    def update_user(user: User, **data) -> User:
        for field, value in data.items():
            if field in ("first_name", "last_name", "email", "username"):
                setattr(user, field, value)
        user.full_clean()
        user.save()
        return user
