import uuid

from django.conf import settings
from django.db import models

from abren_one.modules.organizations.domain.value_objects import (
    MembershipRole,
    MembershipStatus,
)
from abren_one.platform.common.models import TimestampMixin


class Membership(TimestampMixin, models.Model):
    """Connects a global User to an Organization with role and status (§5.1)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.PROTECT,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="organization_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=[(r.value, r.name) for r in MembershipRole],
        default=MembershipRole.MEMBER.value,
        db_index=True,
    )
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.name) for s in MembershipStatus],
        default=MembershipStatus.ACTIVE.value,
        db_index=True,
    )

    class Meta:
        db_table = "organizations_membership"
        ordering = ["organization", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "user"],
                name="unique_organization_user_membership",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} in {self.organization} ({self.role}, {self.status})"

    @property
    def is_active(self) -> bool:
        return self.status == MembershipStatus.ACTIVE.value and self.organization.is_active
