from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from abren_one.platform.identity.interfaces.api.v1.serializers import (
    LoginRequestSerializer,
    UserResponseSerializer,
)


class LoginView(APIView):
    """Authenticate with username/password and establish a Django session."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginRequestSerializer,
        responses={200: UserResponseSerializer},
        description="Login with credentials and receive a session cookie.",
    )
    def post(self, request: Request) -> Response:
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            raise AuthenticationFailed("Invalid username or password.")

        if not user.is_active:
            raise AuthenticationFailed("User account is inactive.")

        login(request, user)
        # Ensure CSRF cookie is set on login response
        get_token(request)
        return Response(UserResponseSerializer(user).data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Terminate the current Django session."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: inline_serializer("LogoutResponse", fields={"detail": serializers.CharField()})},
        description="Log out the current session.",
    )
    def post(self, request: Request) -> Response:
        logout(request)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    """Retrieve details for the currently authenticated user."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: UserResponseSerializer},
        description="Get current authenticated user profile.",
    )
    def get(self, request: Request) -> Response:
        return Response(UserResponseSerializer(request.user).data, status=status.HTTP_200_OK)


class CsrfTokenView(APIView):
    """Return a CSRF token and set the csrftoken cookie."""

    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: inline_serializer("CsrfTokenResponse", fields={"csrfToken": serializers.CharField()})},
        description="Retrieve CSRF token for subsequent mutating requests.",
    )
    def get(self, request: Request) -> Response:
        token = get_token(request)
        return Response({"csrfToken": token}, status=status.HTTP_200_OK)
