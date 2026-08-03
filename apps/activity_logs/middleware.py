import threading

from django.utils.deprecation import MiddlewareMixin

from .models import ActivityLog

_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, "request", None)


class ActivityLoggingMiddleware(MiddlewareMixin):
    EXEMPT_PATHS = ("/admin/", "/static/", "/media/", "/api/schema/", "/api/docs/")

    def process_request(self, request):
        _thread_locals.request = request
        return None

    def process_response(self, request, response):
        path = request.path

        if any(path.startswith(p) for p in self.EXEMPT_PATHS):
            return response
        if not path.startswith("/api/"):
            return response
        if request.method in ("HEAD", "OPTIONS"):
            return response

        user = (
            request.user
            if hasattr(request, "user") and request.user.is_authenticated
            else None
        )

        activity_type = "api_request"
        description = f"{request.method} {path}"

        if hasattr(request, "_activity_type"):
            activity_type = request._activity_type
            description = getattr(request, "_activity_description", description)

        try:
            ActivityLog.objects.create(
                user=user,
                activity_type=activity_type,
                description=description,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                metadata={
                    "method": request.method,
                    "status_code": response.status_code,
                    "path": path,
                },
            )
        except Exception:
            pass

        return response

    def _get_client_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
