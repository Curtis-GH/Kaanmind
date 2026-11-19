"""Management command that creates test accounts with example data.

It helps to try out the API and the frontend. Run it after the migration:

    python manage.py create_demo_data

Test accounts (all with the password ``testpass123``):
    alice@test.de, bob@test.de, carol@test.de
"""

# 1. Third-party
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

# 2. Local
from kanban_app.models import Board, Comment, Task

TEST_PASSWORD = 'testpass123'
TEST_USERS = [
    ('alice@test.de', 'Alice Test'),
    ('bob@test.de', 'Bob Test'),
    ('carol@test.de', 'Carol Test'),
]


def create_users():
    """Create the test accounts and return them as a list."""
    return [
        User.objects.create_user(
            username=email, email=email, password=TEST_PASSWORD,
            first_name=name)
        for email, name in TEST_USERS]


def create_board(alice, bob):
    """Create a board of alice that bob belongs to as well."""
    board = Board.objects.create(title='Demo Board', owner=alice)
    board.members.set([alice, bob])
    return board


def create_tasks(board, alice, bob):
    """Create three tasks with different status and priority."""
    rows = [
        ('Set up project', 'done', 'low', alice, bob),
        ('Write API tests', 'in-progress', 'high', bob, alice),
        ('Write README', 'to-do', 'medium', alice, None),
    ]
    return [
        Task.objects.create(
            board=board, title=title, status=status, priority=priority,
            assignee=assignee, reviewer=reviewer, created_by=alice,
            due_date='2026-12-31')
        for title, status, priority, assignee, reviewer in rows]


class Command(BaseCommand):
    """Create test accounts, a board, tasks and a comment."""

    help = 'Create test accounts and a demo board with tasks.'

    def handle(self, *args, **options):
        """Create the data once. Running it twice changes nothing."""
        if User.objects.filter(username=TEST_USERS[0][0]).exists():
            self.stdout.write('Demo data already exists.')
            return
        alice, bob, carol = create_users()
        board = create_board(alice, bob)
        tasks = create_tasks(board, alice, bob)
        Comment.objects.create(
            task=tasks[1], author=alice, content='Please add more tests.')
        self.stdout.write('Created alice, bob, carol and a demo board.')
