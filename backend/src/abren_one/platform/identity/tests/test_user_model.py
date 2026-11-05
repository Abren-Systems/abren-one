from uuid import UUID

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_with_uuid_pk(self) -> None:
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )
        assert isinstance(user.id, UUID)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpassword123")
        assert user.is_active is True
        assert str(user) == "testuser"

    def test_user_db_table(self) -> None:
        assert User._meta.db_table == "identity_user"
