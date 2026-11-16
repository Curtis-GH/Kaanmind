"""Views for the auth_app API."""

# 1. Third-party
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# 2. Local
from .serializers import LoginSerializer, RegistrationSerializer


def build_auth_data(user):
    """Return token and user data in the format the frontend expects."""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        'token': token.key,
        'fullname': user.first_name,
        'email': user.email,
        'user_id': user.id,
    }


class RegistrationView(APIView):
    """Create a new user account and return a token."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Register a user (201) or report invalid data (400)."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(build_auth_data(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Check the credentials and return a token."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Log a user in (200) or report invalid data (400)."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response(build_auth_data(user), status=status.HTTP_200_OK)
