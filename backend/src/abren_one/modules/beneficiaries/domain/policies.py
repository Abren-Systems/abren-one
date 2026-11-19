"""Domain policies for the Beneficiaries module.

Pure Python business rules governing beneficiary and service delivery lifecycles.
Independent of ORM, database, and transport layers (§2.2).
"""

from __future__ import annotations

from abren_one.modules.beneficiaries.domain.value_objects import (
    BeneficiaryStatus,
    DeliveryStatus,
)

_VALID_BENEFICIARY_TRANSITIONS: dict[BeneficiaryStatus, set[BeneficiaryStatus]] = {
    BeneficiaryStatus.ACTIVE: {
        BeneficiaryStatus.SUSPENDED,
        BeneficiaryStatus.GRADUATED,
        BeneficiaryStatus.ARCHIVED,
    },
    BeneficiaryStatus.SUSPENDED: {
        BeneficiaryStatus.ACTIVE,
        BeneficiaryStatus.ARCHIVED,
    },
    BeneficiaryStatus.GRADUATED: {
        BeneficiaryStatus.ACTIVE,
        BeneficiaryStatus.ARCHIVED,
    },
    BeneficiaryStatus.ARCHIVED: set(),  # Terminal state
}

_VALID_DELIVERY_TRANSITIONS: dict[DeliveryStatus, set[DeliveryStatus]] = {
    DeliveryStatus.PLANNED: {
        DeliveryStatus.DELIVERED,
        DeliveryStatus.CANCELLED,
    },
    DeliveryStatus.DELIVERED: set(),  # Terminal state
    DeliveryStatus.CANCELLED: set(),  # Terminal state
}


def can_transition_beneficiary_status(current: BeneficiaryStatus, target: BeneficiaryStatus) -> bool:
    """Return True if the beneficiary status transition is allowed."""
    if current == target:
        return True
    return target in _VALID_BENEFICIARY_TRANSITIONS.get(current, set())


def can_transition_delivery_status(current: DeliveryStatus, target: DeliveryStatus) -> bool:
    """Return True if the service delivery status transition is allowed."""
    if current == target:
        return True
    return target in _VALID_DELIVERY_TRANSITIONS.get(current, set())
