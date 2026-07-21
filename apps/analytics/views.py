from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AdminDashboardSerializer, UserDashboardSerializer
from .services import AnalyticsService


class UserDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = AnalyticsService.get_user_dashboard(request.user)
        serializer = UserDashboardSerializer(data)
        return Response(serializer.data)


class AdminDashboardView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        data = AnalyticsService.get_admin_dashboard()
        serializer = AdminDashboardSerializer(data)
        return Response(serializer.data)
