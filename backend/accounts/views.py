from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, UserProfileSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]  # noqa: RUF012

    def get(self, request: Request) -> Response:
        """Get the profile of the currently authenticated user.

        Args:
            request (Request): The incoming request object.

        Returns:
            Response: A Response object containing the user's profile data and HTTP status code.
        """
        user = request.user
        if not user:
            return Response(
                {"error": "User not authenticated"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(
            UserProfileSerializer(user).data,
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    permission_classes = []  # noqa: RUF012

    def post(self, request: Request) -> Response:
        """Authenticate a user and return a token.

        Args:
            request (Request): The incoming request object containing the user's credentials.
        """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]  # type: ignore
        password = serializer.validated_data["password"]  # type: ignore

        user = authenticate(request, username=username, password=password)  # pyright: ignore[reportArgumentType]

        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {"token": token.key, "user": UserProfileSerializer(user).data},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )
