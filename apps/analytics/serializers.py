from rest_framework import serializers


class UserDashboardSerializer(serializers.Serializer):
    total_projects = serializers.IntegerField()
    total_downloads = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    recent_activities = serializers.ListField()


class AdminDashboardSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_projects = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    total_downloads = serializers.IntegerField()
    daily_registrations = serializers.ListField()
    daily_uploads = serializers.ListField()
