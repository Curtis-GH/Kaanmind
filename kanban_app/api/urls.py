"""Urls for the kanban_app API."""

# 1. Third-party
from django.urls import path

# 2. Local
from .views import (
    AssignedTasksView, BoardDetailView, BoardListView,
    CommentDeleteView, CommentListView, EmailCheckView,
    ReviewingTasksView, TaskCreateView, TaskDetailView)

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('tasks/', TaskCreateView.as_view(), name='task-create'),
    path('tasks/assigned-to-me/', AssignedTasksView.as_view(),
         name='tasks-assigned'),
    path('tasks/reviewing/', ReviewingTasksView.as_view(),
         name='tasks-reviewing'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/comments/', CommentListView.as_view(),
         name='comment-list'),
    path('tasks/<int:task_id>/comments/<int:pk>/',
         CommentDeleteView.as_view(), name='comment-delete'),
]
