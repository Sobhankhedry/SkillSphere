from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Comment, Project, ProjectFile, Tag

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class ProjectFileSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.CharField(source="uploaded_by.username", read_only=True)

    class Meta:
        model = ProjectFile
        fields = [
            "id",
            "file",
            "original_filename",
            "file_type",
            "file_size",
            "uploaded_by",
            "created_at",
        ]
        read_only_fields = ["id", "file_type", "file_size", "uploaded_by", "created_at"]


class ProjectSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    files = ProjectFileSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        source="tag_name_list",
    )
    invite_usernames = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "owner",
            "owner_username",
            "tags",
            "tag_names",
            "invite_usernames",
            "files",
            "visibility",
            "status",
            "download_count",
            "comments_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "owner_username",
            "download_count",
            "comments_count",
            "created_at",
            "updated_at",
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    project_title = serializers.CharField(source="project.title", read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "project",
            "project_title",
            "author",
            "author_username",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "author_username",
            "project_title",
            "created_at",
            "updated_at",
        ]
