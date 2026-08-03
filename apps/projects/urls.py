from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet, TagViewSet
from .views_invitation import InvitationViewSet, SendInvitationView

router = DefaultRouter()
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"invitations", InvitationViewSet, basename="invitations")
router.register(r"", ProjectViewSet, basename="projects")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "<uuid:project_id>/invite/",
        SendInvitationView.as_view(),
        name="send-invitation",
    ),
]
