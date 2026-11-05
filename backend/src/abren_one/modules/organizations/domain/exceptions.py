class OrganizationError(Exception):
    """Base exception for all domain errors within the organizations module."""


class OrganizationNotFoundError(OrganizationError):
    """Raised when an organization cannot be found."""


class OrganizationSuspendedError(OrganizationError):
    """Raised when an operation is attempted against a suspended organization."""


class MembershipNotFoundError(OrganizationError):
    """Raised when a user membership cannot be found."""


class MembershipInactiveError(OrganizationError):
    """Raised when an operation requires an active membership."""


class DuplicateMembershipError(OrganizationError):
    """Raised when attempting to add a user who is already a member."""


class CannotRevokeLastOwnerError(OrganizationError):
    """Raised when attempting to revoke or demote the last owner of an organization."""
