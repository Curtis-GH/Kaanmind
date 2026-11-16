"""Urls for the kanban_app API."""

# 1. Third-party
from django.urls import path

# 2. Local
from .views import BoardDetailView, BoardListView, EmailCheckView

urlpatterns = [
    path('boards/', BoardListView.as_view(), name='board-list'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]
