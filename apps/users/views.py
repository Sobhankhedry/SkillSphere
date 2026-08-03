from django.contrib.auth import get_user_model
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .services import UserService
from .serializers import GoogleOAuthSerializer
from rest_framework import generics
from .models import Profile
from .serializers import (
    LoginSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
)


User = get_user_model()


class RegisterView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_link = f"{request.scheme}://{request.get_host()}/api/v1/auth/verify-email/{uid}/{token}/"

        from .tasks import send_verification_email

        send_verification_email.delay(str(user.id), user.email, verification_link)

        # اضافه کردن لینک، uid و token مستقیم به پاسخ API برای راحتی تست
        return Response(
            {
                "message": "Registration successful. Please verify your email.",
                "verification_link": verification_link,
                "uid": uid,
                "token": token,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from apps.activity_logs.services import ActivityLogService

        user = User.objects.get(email=serializer.validated_data["email"])
        ActivityLogService.log_activity(
            user=user,
            activity_type="login",
            description=f"User {user.username} logged in",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from apps.activity_logs.services import ActivityLogService

        ActivityLogService.log_activity(
            user=request.user,
            activity_type="logout",
            description=f"User {request.user.username} logged out",
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )
        # Blacklist refresh token
        refresh_token = request.data.get("refresh")
        if refresh_token:
            from rest_framework_simplejwt.tokens import RefreshToken

            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == "admin":
            return Profile.objects.select_related("user").all()
        return Profile.objects.select_related("user").filter(user=self.request.user)

    @action(detail=False, methods=["get", "patch"])
    def me(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if request.method == "PATCH":
            serializer = ProfileUpdateSerializer(
                profile, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            profile.refresh_from_db()
            return Response(ProfileSerializer(profile).data)
        return Response(ProfileSerializer(profile).data)

    @action(detail=False, methods=["get"])
    def by_username(self, request):
        username = request.query_params.get("username")
        if not username:
            return Response(
                {"error": "username parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = UserService.get_user_by_username(username)
        if not user:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(ProfileSerializer(user.profile).data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        q = request.query_params.get("q", "").strip()
        if not q:
            return Response(
                {"error": "q parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        users = (
            User.objects.filter(username__icontains=q)
            .exclude(id=request.user.id)
            .values("id", "username", "first_name", "last_name")[:10]
        )
        return Response(list(users))


class GoogleOAuthView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = GoogleOAuthSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        credential = serializer.validated_data.get("access_token")

        import jwt as pyjwt

        try:
            google_data = pyjwt.decode(credential, options={"verify_signature": False})
        except Exception:
            return Response(
                {"error": "Invalid Google token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = google_data.get("email")
        first_name = google_data.get("given_name", "")
        last_name = google_data.get("family_name", "")

        if not email:
            return Response(
                {"error": "Email not provided by Google"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create or get user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email.split("@")[0],
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
                "email_verified": True,
            },
        )

        if created:
            Profile.objects.get_or_create(user=user)
            if User.objects.filter(username=user.username).count() > 1:
                user.username = f"{user.username}_{str(user.id)[:8]}"
                user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": user.role,
                },
            },
            status=status.HTTP_200_OK,
        )


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_decode
        from django.utils.encoding import force_str

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid verification link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if default_token_generator.check_token(user, token):
            user.email_verified = True
            user.save(update_fields=["email_verified"])
            return Response({"message": "Email verified successfully"})
        return Response(
            {"error": "Invalid or expired verification link"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ResendVerificationEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.email_verified:
            return Response(
                {"message": "Email already verified"},
                status=status.HTTP_200_OK,
            )

        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        verification_link = f"{request.scheme}://{request.get_host()}/api/v1/auth/verify-email/{uid}/{token}/"

        from .tasks import send_verification_email

        send_verification_email.delay(str(user.id), user.email, verification_link)

        return Response({"message": "Verification email sent"})


class RequestPasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(email=email).first()
        if user:
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_encode
            from django.utils.encoding import force_bytes

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{request.scheme}://{request.get_host()}/api/v1/auth/reset-password/{uid}/{token}/"

            from .tasks import send_password_reset_email

            send_password_reset_email.delay(user.email, reset_link)

        return Response({"message": "If the email exists, a reset link has been sent"})


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, uidb64, token):
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_decode
        from django.utils.encoding import force_str

        new_password = request.data.get("new_password")
        if not new_password:
            return Response(
                {"error": "new_password is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid reset link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if default_token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successfully"})
        return Response(
            {"error": "Invalid or expired reset link"},
            status=status.HTTP_400_BAD_REQUEST,
        )
