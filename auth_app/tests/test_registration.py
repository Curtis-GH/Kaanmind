"""Tests for the registration endpoint (POST /api/registration/)."""

# 1. Third-party
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegistrationTests(APITestCase):
    """Check the happy path and every error case of the registration."""

    def setUp(self):
        """Prepare the url and a valid request body."""
        self.url = reverse('registration')
        self.data = {
            'fullname': 'Example Username',
            'email': 'example@mail.de',
            'password': 'examplePassword',
            'repeated_password': 'examplePassword',
        }

    def test_registration_returns_token_and_user_data(self):
        """A valid request returns 201 with token and user data."""
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        keys = {'token', 'fullname', 'email', 'user_id'}
        self.assertEqual(set(response.data), keys)
        self.assertEqual(response.data['fullname'], 'Example Username')

    def test_registration_saves_user_with_email_as_username(self):
        """The user is stored with the email as username."""
        self.client.post(self.url, self.data, format='json')
        user = User.objects.get(username='example@mail.de')
        self.assertEqual(user.first_name, 'Example Username')
        self.assertTrue(user.check_password('examplePassword'))

    def test_registration_does_not_return_password(self):
        """The password must never be part of the response."""
        response = self.client.post(self.url, self.data, format='json')
        self.assertNotIn('password', response.data)

    def test_different_passwords_return_400(self):
        """Two different passwords are rejected."""
        self.data['repeated_password'] = 'somethingElse'
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email_returns_400(self):
        """The same email cannot be registered twice, case ignored."""
        self.client.post(self.url, self.data, format='json')
        self.data['email'] = 'EXAMPLE@mail.de'
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_invalid_email_returns_400(self):
        """An email without a valid format is rejected."""
        self.data['email'] = 'not-an-email'
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_fields_return_400(self):
        """Every field is required."""
        for field in self.data:
            body = {k: v for k, v in self.data.items() if k != field}
            response = self.client.post(self.url, body, format='json')
            self.assertEqual(response.status_code, 400, field)

    def test_registration_ignores_an_invalid_token(self):
        """The endpoint is open, even with a wrong token header."""
        self.client.credentials(HTTP_AUTHORIZATION='Token wrong')
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
