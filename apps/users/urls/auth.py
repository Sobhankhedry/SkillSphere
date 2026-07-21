from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from ..views import (
    GoogleOAuthView,
    LoginView,
    LogoutView,
    RegisterView,
    VerifyEmailView,
    ResendVerificationEmailView,
    RequestPasswordResetView,
    ResetPasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("google/", GoogleOAuthView.as_view(), name="google_oauth"),
    path(
        "verify-email/<str:uidb64>/<str:token>/",
        VerifyEmailView.as_view(),
        name="verify-email",
    ),
    path(
        "resend-verification/",
        ResendVerificationEmailView.as_view(),
        name="resend-verification",
    ),
    path(
        "request-password-reset/",
        RequestPasswordResetView.as_view(),
        name="request-password-reset",
    ),
    path(
        "reset-password/<str:uidb64>/<str:token>/",
        ResetPasswordView.as_view(),
        name="reset-password",
    ),
]
