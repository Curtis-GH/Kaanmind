"""Serializers for the kanban_app API."""

# 1. Third-party
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Show a user with id, email and full name."""

    fullname = serializers.CharField(source='first_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']


class EmailCheckSerializer(serializers.Serializer):
    """Check that the query parameter is a valid email address."""

    email = serializers.EmailField()
