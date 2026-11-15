class FundraisingError(Exception):
    """Base domain exception for the Fundraising module."""


class DonorNotFoundError(FundraisingError):
    """Raised when a donor cannot be found within the active organization."""


class GrantNotFoundError(FundraisingError):
    """Raised when a grant cannot be found within the active organization."""


class DonationNotFoundError(FundraisingError):
    """Raised when a donation cannot be found within the active organization."""


class InvalidDonationAmountError(FundraisingError):
    """Raised when a donation amount is invalid (e.g. <= 0)."""


class InvalidStateTransitionError(FundraisingError):
    """Raised when an entity state transition is disallowed."""


class InactiveDonorError(FundraisingError):
    """Raised when attempting to record a donation or grant against an inactive donor."""


class GrantMismatchError(FundraisingError):
    """Raised when a grant does not match the organization or donor context."""
