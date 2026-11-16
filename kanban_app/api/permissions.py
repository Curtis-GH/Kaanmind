"""Permissions for the kanban_app API."""

# 1. Third-party
from rest_framework.permissions import BasePermission


class IsBoardMember(BasePermission):
    """Allow the owner and the members of a board."""

    def has_object_permission(self, request, view, board):
        """Check if the user belongs to the board."""
        user = request.user
        return board.owner == user or board.members.filter(
            pk=user.pk).exists()


class IsBoardOwner(BasePermission):
    """Allow only the owner of a board."""

    def has_object_permission(self, request, view, board):
        """Check if the user owns the board."""
        return board.owner == request.user
