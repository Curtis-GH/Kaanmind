"""Serializers for the auth_app API."""

# 1. Third-party
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate the registration data and create a new user."""

    fullname = serializers.CharField(max_length=150, write_only=True)
    email = serializers.EmailField(max_length=150)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        """Model and fields of the serializer."""

        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        """Store the email in lower case and reject known addresses."""
        email = value.lower()
        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError(
                'This email address is already registered.')
        return email

    def validate(self, attrs):
        """Check that both password fields are identical."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {'repeated_password': 'The passwords do not match.'})
        return attrs

    def create(self, validated_data):
        """Create the user. The email address is used as username."""
        return User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['fullname'],
        )


class LoginSerializer(serializers.Serializer):
    """Check the email and password of a login request."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the user. Wrong credentials give a 400 error."""
        user = authenticate(
            username=attrs['email'].lower(), password=attrs['password'])
        if user is None:
            raise serializers.ValidationError(
                'The email or the password is incorrect.')
        attrs['user'] = user
        return attrs
