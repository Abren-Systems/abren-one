import uuid

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
class TestIdentityAuthApi:
    def setup_method(self) -> None:
        self.client = APIClient()
        self.password = "StrongPass123!"
        self.user = User.objects.create_user(
            username=f"user_{uuid.uuid4().hex[:8]}",
            email="testuser@example.org",
            password=self.password,
            first_name="Jane",
            last_name="Doe",
        )

    def test_csrf_token_endpoint(self) -> None:
        response = self.client.get("/api/v1/auth/csrf/")
        assert response.status_code == status.HTTP_200_OK
        assert "csrfToken" in response.data
        assert len(response.data["csrfToken"]) > 0

    def test_login_success(self) -> None:
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": self.user.username, "password": self.password},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == self.user.username
        assert response.data["email"] == "testuser@example.org"
        assert response.data["first_name"] == "Jane"
        assert response.data["last_name"] == "Doe"

        # Verify session was created
        me_response = self.client.get("/api/v1/auth/me/")
        assert me_response.status_code == status.HTTP_200_OK
        assert me_response.data["id"] == str(self.user.id)

    def test_login_invalid_credentials_fails(self) -> None:
        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": self.user.username, "password": "wrongpassword"},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN or response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user_fails(self) -> None:
        self.user.is_active = False
        self.user.save()

        response = self.client.post(
            "/api/v1/auth/login/",
            {"username": self.user.username, "password": self.password},
            format="json",
        )
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    def test_logout_success(self) -> None:
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/api/v1/auth/logout/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Successfully logged out."

    def test_logout_unauthenticated_fails(self) -> None:
        response = self.client.post("/api/v1/auth/logout/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED or response.status_code == status.HTTP_403_FORBIDDEN

    def test_me_unauthenticated_fails(self) -> None:
        response = self.client.get("/api/v1/auth/me/")
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
