from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

api_v1_patterns = [
    path("auth/", include("apps.users.urls.auth")),
    path("auth/", include("social_django.urls", namespace="social")),
    path("users/", include("apps.users.urls.profiles")),
    path("projects/", include("apps.projects.urls")),
    path("comments/", include("apps.projects.urls_comments")),
    path("notifications/", include("apps.notifications.urls")),
    path("dashboard/", include("apps.analytics.urls")),
    path("search/", include("apps.search.urls")),
    path("activity-logs/", include("apps.activity_logs.urls")),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(api_v1_patterns)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    try:
        import debug_toolbar  # noqa: F401

        urlpatterns = [
            path("__debug__/", include("debug_toolbar.urls")),
        ] + urlpatterns
    except ImportError:
        pass
