"""Tests for the models of the kanban_app."""

# 1. Third-party
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

# 2. Local
from kanban_app.models import Board, Comment, Task


class ModelTestCase(TestCase):
    """Create the same example data for every model test."""

    def setUp(self):
        """Create two users, a board, a task and a comment."""
        self.owner = User.objects.create_user(
            username='owner@mail.de', email='owner@mail.de', password='pw')
        self.member = User.objects.create_user(
            username='member@mail.de', email='member@mail.de', password='pw')
        self.board = Board.objects.create(title='Project X', owner=self.owner)
        self.task = Task.objects.create(
            board=self.board, title='Write docs', due_date='2026-12-01')
        self.comment = Comment.objects.create(
            task=self.task, author=self.owner, content='First comment')


class BoardTests(ModelTestCase):
    """Check the Board model."""

    def test_str_shows_the_title(self):
        """The text representation is the board title."""
        self.assertEqual(str(self.board), 'Project X')

    def test_members_and_owner_relations(self):
        """Members and owner can be reached from the user."""
        self.board.members.add(self.member)
        self.assertIn(self.board, self.member.boards.all())
        self.assertIn(self.board, self.owner.owned_boards.all())

    def test_deleting_a_board_deletes_tasks_and_comments(self):
        """Tasks and comments of a deleted board are removed as well."""
        self.board.delete()
        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(Comment.objects.count(), 0)


class TaskTests(ModelTestCase):
    """Check the Task model."""

    def test_str_shows_the_title(self):
        """The text representation is the task title."""
        self.assertEqual(str(self.task), 'Write docs')

    def test_defaults(self):
        """A new task is a medium priority to-do without people."""
        self.assertEqual(self.task.status, 'to-do')
        self.assertEqual(self.task.priority, 'medium')
        self.assertIsNone(self.task.assignee)
        self.assertIsNone(self.task.reviewer)

    def test_invalid_status_is_rejected(self):
        """A status outside of the choices fails the validation."""
        self.task.status = 'finished'
        with self.assertRaises(ValidationError):
            self.task.full_clean()

    def test_deleting_the_assignee_keeps_the_task(self):
        """The task stays and its assignee becomes empty."""
        self.task.assignee = self.member
        self.task.save()
        self.member.delete()
        self.task.refresh_from_db()
        self.assertIsNone(self.task.assignee)


class CommentTests(ModelTestCase):
    """Check the Comment model."""

    def test_str_shows_author_and_task(self):
        """The text representation names author and task."""
        self.assertEqual(str(self.comment), 'owner@mail.de on Write docs')

    def test_comments_are_ordered_oldest_first(self):
        """Comments come back in the order they were created."""
        second = Comment.objects.create(
            task=self.task, author=self.owner, content='Second comment')
        self.assertEqual(list(self.task.comments.all()),
                         [self.comment, second])

    def test_deleting_a_task_deletes_its_comments(self):
        """Comments of a deleted task are removed as well."""
        self.task.delete()
        self.assertEqual(Comment.objects.count(), 0)
