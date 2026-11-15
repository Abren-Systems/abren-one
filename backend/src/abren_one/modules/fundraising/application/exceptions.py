"""Application-level exceptions for the Fundraising module (§2.2)."""

from abren_one.modules.fundraising.domain.exceptions import (
    DonationNotFoundError,
    DonorNotFoundError,
    FundraisingError,
    GrantMismatchError,
    GrantNotFoundError,
    InactiveDonorError,
    InvalidDonationAmountError,
    InvalidStateTransitionError,
)

__all__ = [
    "DonationNotFoundError",
    "DonorNotFoundError",
    "FundraisingError",
    "GrantMismatchError",
    "GrantNotFoundError",
    "InactiveDonorError",
    "InvalidDonationAmountError",
    "InvalidStateTransitionError",
]
