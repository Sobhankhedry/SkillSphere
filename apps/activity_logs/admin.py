from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ["user", "activity_type", "description", "ip_address", "created_at"]
    list_filter = ["activity_type"]
    search_fields = ["user__username", "description"]
    raw_id_fields = ["user"]
    readonly_fields = ["metadata"]
