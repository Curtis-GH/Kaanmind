"""Views for the kanban_app API."""

# 1. Third-party
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# 2. Local
from kanban_app.models import Board, Comment, Task
from .permissions import (
    IsBoardMember, IsBoardOwner, IsCommentAuthor,
    IsTaskBoardMember, IsTaskCreatorOrBoardOwner)
from .serializers import (
    BoardDetailSerializer, BoardListSerializer, BoardUpdateSerializer,
    CommentSerializer, EmailCheckSerializer, TaskSerializer,
    TaskUpdateSerializer, UserSerializer)


class BoardListView(generics.ListCreateAPIView):
    """List the boards of the user or create a new board."""

    permission_classes = [IsAuthenticated]
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

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the user with the given email or an error."""
        serializer = EmailCheckSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].lower()
        user = User.objects.filter(email=email).first()
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user).data)


class TaskCreateView(generics.CreateAPIView):
    """Create a task on a board where the user is a member."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def check_board_access(self, board_id):
        """Answer 404 for an unknown board and 403 for a stranger."""
        if not str(board_id).isdigit():
            raise ValidationError({'board': 'A valid board id is needed.'})
        board = get_object_or_404(Board, pk=board_id)
        if not IsBoardMember().has_object_permission(
                self.request, self, board):
            raise PermissionDenied('You are not a member of this board.')

    def create(self, request, *args, **kwargs):
        """Check the board first, then create the task."""
        self.check_board_access(request.data.get('board'))
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Remember who created the task."""
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.UpdateAPIView, generics.DestroyAPIView):
    """Change or delete one task."""

    queryset = Task.objects.all()
    serializer_class = TaskUpdateSerializer
    http_method_names = ['patch', 'delete']

    def get_permissions(self):
        """Members may change, creator and board owner may delete."""
        if self.request.method == 'DELETE':
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated(), IsTaskBoardMember()]


class AssignedTasksView(generics.ListAPIView):
    """List the tasks that are assigned to the user."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        """Return tasks where the user is the assignee."""
        return Task.objects.filter(assignee=self.request.user)


class ReviewingTasksView(generics.ListAPIView):
    """List the tasks that the user has to review."""

    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        """Return tasks where the user is the reviewer."""
        return Task.objects.filter(reviewer=self.request.user)


class CommentListView(generics.ListCreateAPIView):
    """List the comments of a task or add a new one."""

    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_task(self):
        """Find the task; only members of its board may use it."""
        task = get_object_or_404(Task, pk=self.kwargs['task_id'])
        if not IsTaskBoardMember().has_object_permission(
                self.request, self, task):
            raise PermissionDenied('You are not a member of this board.')
        return task

    def get_queryset(self):
        """Return the comments of the task, oldest first."""
        return self.get_task().comments.all()

    def perform_create(self, serializer):
        """Set task and author of the new comment."""
        serializer.save(task=self.get_task(), author=self.request.user)


class CommentDeleteView(generics.DestroyAPIView):
    """Delete a comment; only the author may do it."""

    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_queryset(self):
        """Only comments of the task in the url can be found."""
        return Comment.objects.filter(task_id=self.kwargs['task_id'])
