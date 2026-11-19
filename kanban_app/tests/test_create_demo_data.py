"""Tests for the create_demo_data command."""

# 1. Third-party
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

# 2. Local
from kanban_app.models import Board, Comment, Task


class CreateDemoDataTests(TestCase):
    """Check that the demo data is created once."""

    def test_creates_accounts_board_tasks_and_comment(self):
        """Three users, one board, three tasks and one comment exist."""
        call_command('create_demo_data')
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Board.objects.get().members.count(), 2)
        self.assertEqual(Task.objects.count(), 3)
        self.assertEqual(Comment.objects.count(), 1)

    def test_test_account_can_log_in(self):
        """The password of the test accounts works."""
        call_command('create_demo_data')
        self.assertTrue(
            self.client.login(username='alice@test.de',
                              password='testpass123'))

    def test_running_twice_changes_nothing(self):
        """The second run does not create duplicates."""
        call_command('create_demo_data')
        call_command('create_demo_data')
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Board.objects.count(), 1)
