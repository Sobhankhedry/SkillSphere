from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FeedbackViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r"", NotificationViewSet, basename="notifications")
router.register(r"feedbacks", FeedbackViewSet, basename="feedbacks")

urlpatterns = [
    path("", include(router.urls)),
]
