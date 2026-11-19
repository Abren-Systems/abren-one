"""Application-level exceptions for the Beneficiaries module (§2.2)."""

from abren_one.modules.beneficiaries.domain.exceptions import (
    BeneficiaryError,
    BeneficiaryNotFoundError,
    InactiveBeneficiaryError,
    InvalidBeneficiaryTransitionError,
    InvalidDeliveryTransitionError,
    ServiceDeliveryNotFoundError,
)

__all__ = [
    "BeneficiaryError",
    "BeneficiaryNotFoundError",
    "InactiveBeneficiaryError",
    "InvalidBeneficiaryTransitionError",
    "InvalidDeliveryTransitionError",
    "ServiceDeliveryNotFoundError",
]
