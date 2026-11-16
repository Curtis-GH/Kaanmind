"""Models of the kanban_app: boards, tasks and comments."""

# 1. Third-party
from django.contrib.auth.models import User
from django.db import models


class Board(models.Model):
    """A Kanban board with one owner and any number of members."""

    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField(
        User, related_name='boards', blank=True)

    class Meta:
        verbose_name = 'Board'
        verbose_name_plural = 'Boards'
        ordering = ['title']

    def __str__(self):
        """Show the title of the board."""
        return self.title


class Task(models.Model):
    """A task on a board with status, priority and responsible people."""

    STATUS_CHOICES = [
        ('to-do', 'To do'),
        ('in-progress', 'In progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='to-do')
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default='medium')
    assignee = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_tasks')
    reviewer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='review_tasks')
    due_date = models.DateField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_tasks')

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['id']

    def __str__(self):
        """Show the title of the task."""
        return self.title
