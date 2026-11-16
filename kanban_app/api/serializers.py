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


class BoardListSerializer(serializers.ModelSerializer):
    """List and create boards with their counters."""

    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(),
        write_only=True, required=False)
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'member_count', 'ticket_count',
                  'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id']

    def get_member_count(self, board):
        """Count the members of the board."""
        return board.members.count()

    def get_ticket_count(self, board):
        """Count all tasks of the board."""
        return board.tasks.count()

    def get_tasks_to_do_count(self, board):
        """Count the tasks that still have the status to-do."""
        return board.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, board):
        """Count the tasks with high priority."""
        return board.tasks.filter(priority='high').count()

    def create(self, validated_data):
        """Save the board and make the owner a member as well."""
        members = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)
        board.members.set(members + [board.owner])
        return board


class BoardDetailSerializer(serializers.ModelSerializer):
    """Show one board with its members and tasks."""

    owner_id = serializers.IntegerField(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    tasks = BoardTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class BoardUpdateSerializer(serializers.ModelSerializer):
    """Change title and members of a board."""

    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), write_only=True)
    owner_data = UserSerializer(source='owner', read_only=True)
    members_data = UserSerializer(
        source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']

    def update(self, board, validated_data):
        """Save the changes and keep the owner as a member."""
        members = validated_data.pop('members', None)
        board = super().update(board, validated_data)
        if members is not None:
            board.members.set(members + [board.owner])
        return board
