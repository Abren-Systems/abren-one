from decimal import Decimal

import pytest

from abren_one.modules.fundraising.domain.exceptions import (
    InactiveDonorError,
    InvalidDonationAmountError,
    InvalidStateTransitionError,
)
from abren_one.modules.fundraising.domain.policies import (
    validate_donation_amount,
    validate_donation_transition,
    validate_donor_active,
    validate_grant_transition,
)


class TestDonationAmountValidation:
    def test_positive_amounts_pass(self) -> None:
        validate_donation_amount(Decimal("0.01"))
        validate_donation_amount(Decimal("100.00"))
        validate_donation_amount(Decimal("5000000.50"))

    def test_zero_amount_fails(self) -> None:
        with pytest.raises(InvalidDonationAmountError):
            validate_donation_amount(Decimal("0.00"))

    def test_negative_amount_fails(self) -> None:
        with pytest.raises(InvalidDonationAmountError):
            validate_donation_amount(Decimal("-10.00"))


class TestDonorActiveValidation:
    def test_active_donor_passes(self) -> None:
        validate_donor_active(True)

    def test_inactive_donor_fails(self) -> None:
        with pytest.raises(InactiveDonorError):
            validate_donor_active(False)


class TestGrantTransitions:
    @pytest.mark.parametrize(
        ("current", "target"),
        [
            ("proposed", "awarded"),
            ("proposed", "closed"),
            ("awarded", "active"),
            ("awarded", "closed"),
            ("active", "completed"),
            ("active", "closed"),
            ("completed", "closed"),
        ],
    )
    def test_valid_grant_transitions(self, current: str, target: str) -> None:
        validate_grant_transition(current, target)

    @pytest.mark.parametrize(
        ("current", "target"),
        [
            ("proposed", "active"),
            ("proposed", "completed"),
            ("completed", "active"),
            ("closed", "active"),
            ("closed", "proposed"),
        ],
    )
    def test_invalid_grant_transitions_fail(self, current: str, target: str) -> None:
        with pytest.raises(InvalidStateTransitionError):
            validate_grant_transition(current, target)


class TestDonationTransitions:
    @pytest.mark.parametrize(
        ("current", "target"),
        [
            ("received", "confirmed"),
            ("received", "refunded"),
            ("confirmed", "refunded"),
        ],
    )
    def test_valid_donation_transitions(self, current: str, target: str) -> None:
        validate_donation_transition(current, target)

    @pytest.mark.parametrize(
        ("current", "target"),
        [
            ("refunded", "confirmed"),
            ("refunded", "received"),
            ("confirmed", "received"),
        ],
    )
    def test_invalid_donation_transitions_fail(self, current: str, target: str) -> None:
        with pytest.raises(InvalidStateTransitionError):
            validate_donation_transition(current, target)
