import pytest


@pytest.mark.django_db
class TestLogin:

    def test_login_success(self, api_client, seeker_user):
        data = {"email": "seeker@test.com", "password": "testpass123"}

        response = api_client.post("/auth/login", data, format="json")

        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["email"] == "seeker@test.com"
        assert response.data["user"]["role"] == "SEEKER"

    def test_login_unverified_user(self, api_client, unverified_user):
        data = {"email": "unverified@test.com", "password": "testpass123"}

        response = api_client.post("/auth/login", data, format="json")

        assert response.status_code == 400
        assert "not verified" in response.data["detail"].lower()

    def test_login_invalid_credentials(self, api_client, seeker_user):
        data = {"email": "seeker@test.com", "password": "wrongpassword"}

        response = api_client.post("/auth/login", data, format="json")

        assert response.status_code == 400

    def test_login_nonexistent_user(self, api_client):
        data = {"email": "nonexistent@test.com", "password": "testpass123"}

        response = api_client.post("/auth/login", data, format="json")

        assert response.status_code == 400

    def test_token_refresh(self, api_client, seeker_user):
        login_data = {"email": "seeker@test.com", "password": "testpass123"}

        login_response = api_client.post("/auth/login", login_data, format="json")
        refresh_token = login_response.data["refresh"]

        refresh_data = {"refresh": refresh_token}

        response = api_client.post("/auth/refresh", refresh_data, format="json")

        assert response.status_code == 200
        assert "access" in response.data
