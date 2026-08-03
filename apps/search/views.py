from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    SearchProjectSerializer,
    SearchResultSerializer,
    SearchUserSerializer,
)
from .services import SearchService


class GlobalSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response(
                {"error": "Search query is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user if request.user.is_authenticated else None
        results = SearchService.global_search(query, user)
        serializer = SearchResultSerializer(results)
        return Response(serializer.data)


class ProjectSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response(
                {"error": "Search query is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user if request.user.is_authenticated else None
        projects = SearchService.search_projects(query, user)
        serializer = SearchProjectSerializer(projects[:20], many=True)
        return Response(serializer.data)


class UserSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response(
                {"error": "Search query is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        users = SearchService.search_users(query)
        serializer = SearchUserSerializer(users[:20], many=True)
        return Response(serializer.data)
