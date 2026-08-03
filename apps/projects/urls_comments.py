from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views_comments import CommentViewSet

router = DefaultRouter()
router.register(r"", CommentViewSet, basename="comments")

urlpatterns = [
    path("", include(router.urls)),
]
