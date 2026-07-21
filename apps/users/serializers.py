from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Profile
from .services import UserService

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name",
            "role", "is_active", "email_verified", "created_at",
        ]
        read_only_fields = ["id", "role", "is_active", "email_verified", "created_at"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id", "user", "bio", "avatar", "github_link",
            "linkedin_link", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(min_length=3, max_length=150)
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirm = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, default="")
    last_name = serializers.CharField(max_length=150, required=False, default="")

    def validate_username(self, value):
        if not value.isalnum() and "_" not in value:
            raise serializers.ValidationError(
                "Username must contain only letters, numbers, and underscores"
            )
        return value.lower()

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        return UserService.register_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)

    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Incorrect password")
        return value


class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name", required=False)
    last_name = serializers.CharField(source="user.last_name", required=False)

    class Meta:
        model = Profile
        fields = [
            "first_name", "last_name", "bio", "avatar",
            "github_link", "linkedin_link",
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        if user_data:
            UserService.update_user(instance.user, **user_data)
        return UserService.update_profile(instance.user, **validated_data)
