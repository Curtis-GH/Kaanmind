"""Admin configuration of the kanban_app."""

# 1. Third-party
from django.contrib import admin

# 2. Local
from .models import Board, Comment, Task


class BoardAdmin(admin.ModelAdmin):
    """Show boards with their owner and filter them by owner."""

    list_display = ['title', 'owner']
    list_filter = ['owner']


class TaskAdmin(admin.ModelAdmin):
    """Show tasks with status, priority and due date."""

    list_display = ['title', 'board', 'status', 'priority', 'due_date']
    list_filter = ['status', 'priority', 'board']


class CommentAdmin(admin.ModelAdmin):
    """Show comments with author and creation time."""

    list_display = ['task', 'author', 'created_at']
    list_filter = ['task']
    readonly_fields = ['created_at']


admin.site.register(Board, BoardAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Comment, CommentAdmin)
