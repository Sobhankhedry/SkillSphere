from django.urls import path

from .views import AdminDashboardView, UserDashboardView

urlpatterns = [
    path("user/", UserDashboardView.as_view(), name="user-dashboard"),
    path("admin/", AdminDashboardView.as_view(), name="admin-dashboard"),
]
