"""Views for the kanban_app API."""

# 1. Third-party
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# 2. Local
from kanban_app.models import Board
from .permissions import IsBoardMember, IsBoardOwner
from .serializers import (
    BoardDetailSerializer, BoardListSerializer, BoardUpdateSerializer,
    EmailCheckSerializer, UserSerializer)


class BoardListView(generics.ListCreateAPIView):
    """List the boards of the user or create a new board."""

    serializer_class = BoardListSerializer

    def get_queryset(self):
        """Return boards where the user is owner or member."""
        user = self.request.user
        return Board.objects.filter(
            Q(owner=user) | Q(members=user)).distinct()

    def perform_create(self, serializer):
        """Make the logged in user the owner."""
        serializer.save(owner=self.request.user)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Show, change or delete one board."""

    queryset = Board.objects.all()
    http_method_names = ['get', 'patch', 'delete']

    def get_serializer_class(self):
        """Use the update serializer only for changes."""
        if self.request.method == 'PATCH':
            return BoardUpdateSerializer
        return BoardDetailSerializer

    def get_permissions(self):
        """Only the owner may delete, members may see and change."""
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsBoardOwner()]
        return [IsAuthenticated(), IsBoardMember()]


class EmailCheckView(APIView):
    """Find a user by email address."""

    def get(self, request):
        """Return the user with the given email or an error."""
        serializer = EmailCheckSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower()
        user = User.objects.filter(email=email).first()
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user).data)
