"""Serializers for the kanban_app API."""

# 1. Third-party
from django.contrib.auth.models import User
from rest_framework import serializers

# 2. Local
from kanban_app.models import Board, Task


class UserSerializer(serializers.ModelSerializer):
    """Show a user with id, email and full name."""

    fullname = serializers.CharField(source='first_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']


class EmailCheckSerializer(serializers.Serializer):
    """Check that the query parameter is a valid email address."""

    email = serializers.EmailField()


class BoardTaskSerializer(serializers.ModelSerializer):
    """Show a task inside the detail view of a board."""

    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority',
                  'assignee', 'reviewer', 'due_date', 'comments_count']

    def get_comments_count(self, task):
        """Count the comments of the task."""
        return task.comments.count()
