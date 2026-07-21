from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ..views import ProfileViewSet

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet, basename="profiles")

urlpatterns = [
    path("", include(router.urls)),
]
