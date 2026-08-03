from django.contrib import admin

from .models import Comment, Project, ProjectFile, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "created_at"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "owner",
        "visibility",
        "status",
        "download_count",
        "created_at",
    ]
    list_filter = ["visibility", "status"]
    search_fields = ["title", "owner__username"]
    autocomplete_fields = ["owner"]
    filter_horizontal = ["tags"]


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = [
        "original_filename",
        "project",
        "file_type",
        "file_size",
        "uploaded_by",
    ]
    list_filter = ["file_type"]
    raw_id_fields = ["project", "uploaded_by"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "project", "content", "created_at"]
    raw_id_fields = ["author", "project"]
