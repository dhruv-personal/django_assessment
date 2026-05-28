from datetime import timedelta

from django.utils import timezone

import pytest

from authentication.models import OTP


@pytest.mark.django_db
class TestVerification:

    def test_verify_email_success(self, api_client, unverified_user):
        otp = OTP.objects.create(user=unverified_user, code="123456", expires_at=timezone.now() + timedelta(minutes=5))

        data = {"email": unverified_user.email, "otp": "123456"}

        response = api_client.post("/auth/verify-email", data, format="json")

        assert response.status_code == 200
        assert "verified successfully" in response.data["detail"]

        unverified_user.profile.refresh_from_db()
        assert unverified_user.profile.email_verified

        otp.refresh_from_db()
        assert otp.is_used

    def test_verify_email_invalid_otp(self, api_client, unverified_user):
        OTP.objects.create(user=unverified_user, code="123456", expires_at=timezone.now() + timedelta(minutes=5))

        data = {"email": unverified_user.email, "otp": "999999"}

        response = api_client.post("/auth/verify-email", data, format="json")

        assert response.status_code == 400

    def test_verify_email_expired_otp(self, api_client, unverified_user):
        OTP.objects.create(user=unverified_user, code="123456", expires_at=timezone.now() - timedelta(minutes=1))

        data = {"email": unverified_user.email, "otp": "123456"}

        response = api_client.post("/auth/verify-email", data, format="json")

        assert response.status_code == 400
        assert "expired" in response.data["detail"].lower()

    def test_verify_email_max_attempts(self, api_client, unverified_user):
        otp = OTP.objects.create(
            user=unverified_user, code="123456", expires_at=timezone.now() + timedelta(minutes=5), attempts=3
        )

        data = {"email": unverified_user.email, "otp": "123456"}

        response = api_client.post("/auth/verify-email", data, format="json")

        assert response.status_code == 400
        assert "attempts" in response.data["detail"].lower()

    def test_verify_email_user_not_found(self, api_client):
        data = {"email": "nonexistent@test.com", "otp": "123456"}

        response = api_client.post("/auth/verify-email", data, format="json")

        assert response.status_code == 400
