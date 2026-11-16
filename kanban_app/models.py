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
