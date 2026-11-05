"""
Custom user model for Abren One.

Established before the first migration per architectural contract.
A user is a global identity — not an organization. Users connect
to organizations through OrganizationMembership.
"""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for Abren One.

    Uses UUID primary key. Organizational attributes belong in
    the Organizations module (memberships), not here.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        db_table = "identity_user"

    def __str__(self) -> str:
        return self.username or str(self.id)
