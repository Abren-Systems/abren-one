from decimal import Decimal

from abren_one.modules.fundraising.domain.exceptions import (
    InactiveDonorError,
    InvalidDonationAmountError,
    InvalidStateTransitionError,
)
from abren_one.modules.fundraising.domain.value_objects import (
    DonationStatus,
    GrantStatus,
)

_VALID_GRANT_TRANSITIONS: dict[GrantStatus, set[GrantStatus]] = {
    GrantStatus.PROPOSED: {GrantStatus.AWARDED, GrantStatus.CLOSED},
    GrantStatus.AWARDED: {GrantStatus.ACTIVE, GrantStatus.CLOSED},
    GrantStatus.ACTIVE: {GrantStatus.COMPLETED, GrantStatus.CLOSED},
    GrantStatus.COMPLETED: {GrantStatus.CLOSED},
    GrantStatus.CLOSED: set(),
}

_VALID_DONATION_TRANSITIONS: dict[DonationStatus, set[DonationStatus]] = {
    DonationStatus.RECEIVED: {DonationStatus.CONFIRMED, DonationStatus.REFUNDED},
    DonationStatus.CONFIRMED: {DonationStatus.REFUNDED},
    DonationStatus.REFUNDED: set(),
}


def validate_donation_amount(amount: Decimal) -> None:
    """Validate that the donation amount is strictly positive (§Appendix B)."""
    if amount <= Decimal("0"):
        raise InvalidDonationAmountError("Donation amount must be strictly greater than zero.")


def validate_donor_active(is_active: bool) -> None:
    """Validate that the donor is active before accepting funds."""
    if not is_active:
        raise InactiveDonorError("Cannot accept donations or create grants for an inactive donor.")


def validate_grant_transition(current: str, target: str) -> None:
    """Validate that a grant lifecycle state transition is permitted."""
    curr_status = GrantStatus(current)
    tgt_status = GrantStatus(target)
    allowed = _VALID_GRANT_TRANSITIONS.get(curr_status, set())
    if tgt_status not in allowed:
        raise InvalidStateTransitionError(
            f"Cannot transition grant from '{curr_status.value}' to '{tgt_status.value}'."
        )


def validate_donation_transition(current: str, target: str) -> None:
    """Validate that a donation status transition is permitted."""
    curr_status = DonationStatus(current)
    tgt_status = DonationStatus(target)
    allowed = _VALID_DONATION_TRANSITIONS.get(curr_status, set())
    if tgt_status not in allowed:
        raise InvalidStateTransitionError(
            f"Cannot transition donation from '{curr_status.value}' to '{tgt_status.value}'."
        )
