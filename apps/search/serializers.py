from rest_framework import serializers


class SearchResultSerializer(serializers.Serializer):
    projects = serializers.ListField()
    users = serializers.ListField()
    tags = serializers.ListField()


class SearchProjectSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    owner_username = serializers.CharField()
    tags = serializers.ListField(child=serializers.DictField(), default=[])
    download_count = serializers.IntegerField(default=0)


class SearchUserSerializer(serializers.Serializer):
    id = serializers.CharField()
    username = serializers.CharField()
    first_name = serializers.CharField(default="")
    last_name = serializers.CharField(default="")
