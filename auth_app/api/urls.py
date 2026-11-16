"""Urls for the auth_app API."""

# 1. Third-party
from django.urls import path

# 2. Local
from .views import RegistrationView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
]
