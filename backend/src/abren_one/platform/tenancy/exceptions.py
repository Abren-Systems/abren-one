class TenancyError(Exception):
    """Base exception for tenancy errors."""


class TenantContextMissingError(TenancyError):
    """Raised when an operation requires an organization context that is missing."""


class TenantContextInvalidError(TenancyError):
    """Raised when an organization identifier is malformed or invalid."""


class TenantMembershipRequiredError(TenancyError):
    """Raised when a user is not a member of the requested organization."""


class TenantInactiveError(TenancyError):
    """Raised when the organization or user's membership is inactive/suspended."""
