"""Exceptions for the Procurement domain."""

from __future__ import annotations

from abren_one.platform.common.exceptions import DomainError, NotFoundError


class ProcurementError(DomainError):
    """Base exception for domain errors in Procurement."""


class VendorNotFoundError(NotFoundError, ProcurementError):
    """Raised when a vendor is not found in the current organization."""


class RequisitionNotFoundError(NotFoundError, ProcurementError):
    """Raised when a purchase requisition is not found in the current organization."""


class PurchaseOrderNotFoundError(NotFoundError, ProcurementError):
    """Raised when a purchase order is not found in the current organization."""


class GoodsReceiptNotFoundError(NotFoundError, ProcurementError):
    """Raised when a goods receipt note is not found in the current organization."""


class InvalidRequisitionTransitionError(ProcurementError):
    """Raised when a requisition authorization status transition is invalid."""


class InvalidPurchaseOrderTransitionError(ProcurementError):
    """Raised when a purchase order status transition is invalid."""


class InactiveVendorError(ProcurementError):
    """Raised when an operation targets an inactive vendor."""


class EmptyRequisitionError(ProcurementError):
    """Raised when a requisition has no items."""


class SelfApprovalError(ProcurementError):
    """Raised when a requester attempts to approve their own requisition."""


class OrganizationMismatchError(ProcurementError):
    """Raised when related entities belong to different organizations."""


class InspectionQuantityError(ProcurementError):
    """Raised when inspection quantities fail reconciliation."""


class OverAllocationError(ProcurementError):
    """Raised when allocation would exceed the requested quantity."""


class OverReceiptError(ProcurementError):
    """Raised when receipt would exceed the ordered quantity."""


class CancellationBlockedError(ProcurementError):
    """Raised when a PO cannot be cancelled due to accepted receipts."""
