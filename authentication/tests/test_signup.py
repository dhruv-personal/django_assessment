from django.contrib.auth.models import User
from django.core import mail

import pytest

from authentication.models import OTP, UserProfile


@pytest.mark.django_db
class TestSignup:

    def test_signup_success(self, api_client):
        data = {"email": "newuser@test.com", "password": "SecurePass123!", "role": "SEEKER"}

        response = api_client.post("/auth/signup", data, format="json")

        assert response.status_code == 201
        assert "OTP sent to email" in response.data["detail"]
        assert User.objects.filter(email="newuser@test.com").exists()

        user = User.objects.get(email="newuser@test.com")
        assert user.profile.role == UserProfile.SEEKER
        assert not user.profile.email_verified
        assert OTP.objects.filter(user=user).exists()

    def test_signup_duplicate_email(self, api_client, seeker_user):
        data = {"email": "seeker@test.com", "password": "SecurePass123!", "role": "SEEKER"}

        response = api_client.post("/auth/signup", data, format="json")

        assert response.status_code == 400

    def test_signup_weak_password(self, api_client):
        data = {"email": "newuser@test.com", "password": "123", "role": "SEEKER"}

        response = api_client.post("/auth/signup", data, format="json")

        assert response.status_code == 400

    def test_signup_facilitator_role(self, api_client):
        data = {"email": "facilitator_new@test.com", "password": "SecurePass123!", "role": "FACILITATOR"}

        response = api_client.post("/auth/signup", data, format="json")

        assert response.status_code == 201
        user = User.objects.get(email="facilitator_new@test.com")
        assert user.profile.role == UserProfile.FACILITATOR

    def test_signup_sends_otp_email(self, api_client):
        data = {"email": "newuser@test.com", "password": "SecurePass123!", "role": "SEEKER"}

        response = api_client.post("/auth/signup", data, format="json")

        assert response.status_code == 201
        assert len(mail.outbox) == 1
        assert "OTP" in mail.outbox[0].subject or "Verification" in mail.outbox[0].subject
