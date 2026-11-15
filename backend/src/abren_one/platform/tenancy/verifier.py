from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class MembershipInfo:
    """Snapshot of user membership within an organization."""

    organization_id: UUID
    user_id: UUID
    role: str
    status: str
    is_active: bool


class MembershipVerifier(Protocol):
    """Protocol for checking user membership in an organization (§5.5).

    Implemented by the Organizations module and registered with Tenancy.
    This maintains the architectural rule that platform does not import modules.
    """

    def get_membership(self, *, user_id: UUID, organization_id: UUID) -> MembershipInfo | None: ...


_verifier: MembershipVerifier | None = None


def register_membership_verifier(verifier: MembershipVerifier) -> None:
    """Register the system-wide membership verifier."""
    global _verifier
    _verifier = verifier


def get_membership_verifier() -> MembershipVerifier | None:
    """Get the currently registered membership verifier."""
    return _verifier


def verify_user_membership(user_id: UUID, organization_id: UUID) -> MembershipInfo | None:
    """Look up membership using the registered verifier.

    Returns None when the user has no membership or if no verifier has been registered,
    ensuring fail-closed access (§5.4, §5.5).
    """
    if _verifier is None:
        return None
    return _verifier.get_membership(user_id=user_id, organization_id=organization_id)
