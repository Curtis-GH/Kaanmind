"""Tests for the login endpoint (POST /api/login/)."""

# 1. Third-party
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class LoginTests(APITestCase):
    """Check the happy path and every error case of the login."""

    def setUp(self):
        """Create a user and prepare the url and a valid request body."""
        self.user = User.objects.create_user(
            username='example@mail.de', email='example@mail.de',
            password='examplePassword', first_name='Example Username')
        self.url = reverse('login')
        self.data = {'email': 'example@mail.de',
                     'password': 'examplePassword'}

    def test_login_returns_token_and_user_data(self):
        """Correct credentials return 200 with token and user data."""
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_id'], self.user.id)
        self.assertEqual(response.data['fullname'], 'Example Username')
        self.assertEqual(response.data['email'], 'example@mail.de')

    def test_login_returns_the_token_of_the_user(self):
        """The returned token belongs to the user and is reused."""
        response = self.client.post(self.url, self.data, format='json')
        token = Token.objects.get(user=self.user)
        self.assertEqual(response.data['token'], token.key)

    def test_login_ignores_upper_case_in_email(self):
        """The email is not case sensitive."""
        self.data['email'] = 'EXAMPLE@mail.de'
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_password_returns_400(self):
        """A wrong password is rejected with 400."""
        self.data['password'] = 'wrongPassword'
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_email_returns_400(self):
        """An unknown email is rejected with 400."""
        self.data['email'] = 'unknown@mail.de'
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_fields_return_400(self):
        """Email and password are both required."""
        for field in self.data:
            body = {k: v for k, v in self.data.items() if k != field}
            response = self.client.post(self.url, body, format='json')
            self.assertEqual(response.status_code, 400, field)
