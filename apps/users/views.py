"""
API views for user authentication.
"""

from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from common.constants import SuccessMessages

from .serializers import LoginSerializer, UserSerializer
from .services import AuthService


class LoginView(APIView):
    """POST /api/v1/auth/login/

    Authenticate with username + password and receive a session cookie.
    """

    permission_classes = [AllowAny]
    authentication_classes: list = []  # Skip session auth for login

    def post(self, request: Request) -> Response:
        """Handle login request.

        Args:
            request: DRF request containing ``username`` and ``password``.

        Returns:
            200 on success with user details, 400 on invalid credentials.
        """
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        AuthService.login(request, user)

        return Response(
            {
                "success": True,
                "message": SuccessMessages.LOGIN_SUCCESS,
                "data": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """POST /api/v1/auth/logout/

    Destroy the current session.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Handle logout request.

        Args:
            request: DRF request with active session.

        Returns:
            200 on success.
        """
        AuthService.logout(request)
        return Response(
            {
                "success": True,
                "message": SuccessMessages.LOGOUT_SUCCESS,
            },
            status=status.HTTP_200_OK,
        )
