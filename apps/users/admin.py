from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Profile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ["email", "username", "role", "is_active", "email_verified", "created_at"]
    list_filter = ["role", "is_active", "email_verified"]
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2", "role"),
        }),
    )
    search_fields = ["email", "username"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "username")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "role", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at")}),
        ("Additional Info", {"fields": ("email_verified",)}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "github_link", "linkedin_link", "created_at"]
    search_fields = ["user__username", "user__email"]
    autocomplete_fields = ["user"]
