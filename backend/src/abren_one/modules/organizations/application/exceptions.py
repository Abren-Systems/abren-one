"""Application-level exceptions for the Organizations module.

Re-exports domain exceptions so interfaces interact only with the application layer (§2.2).
"""

from abren_one.modules.organizations.domain.exceptions import (
    CannotRevokeLastOwnerError,
    DuplicateMembershipError,
    MembershipInactiveError,
    MembershipNotFoundError,
    OrganizationError,
    OrganizationNotFoundError,
    OrganizationSuspendedError,
)

__all__ = [
    "CannotRevokeLastOwnerError",
    "DuplicateMembershipError",
    "MembershipInactiveError",
    "MembershipNotFoundError",
    "OrganizationError",
    "OrganizationNotFoundError",
    "OrganizationSuspendedError",
]
