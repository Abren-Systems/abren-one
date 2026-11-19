from abren_one.platform.common.exceptions import DomainError, NotFoundError


class BeneficiaryError(DomainError):
    """Base domain exception for the Beneficiaries module."""


class BeneficiaryNotFoundError(NotFoundError, BeneficiaryError):
    """Raised when a beneficiary cannot be found within the active organization."""


class ServiceDeliveryNotFoundError(NotFoundError, BeneficiaryError):
    """Raised when a service delivery record cannot be found within the active organization."""


class InvalidBeneficiaryTransitionError(BeneficiaryError):
    """Raised when an entity lifecycle transition is disallowed."""


class InvalidDeliveryTransitionError(BeneficiaryError):
    """Raised when a service delivery status transition is disallowed."""


class InactiveBeneficiaryError(BeneficiaryError):
    """Raised when an operation requires an active beneficiary."""
