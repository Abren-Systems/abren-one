"""Domain policies and invariants for the Procurement module.

Pure Python business rules governing procurement lifecycles.
Independent of ORM, database, and transport layers.
"""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from abren_one.modules.procurement.domain.exceptions import (
    CancellationBlockedError,
    EmptyRequisitionError,
    InactiveVendorError,
    InspectionQuantityError,
    InvalidPurchaseOrderTransitionError,
    InvalidRequisitionTransitionError,
    OverAllocationError,
    OverReceiptError,
    SelfApprovalError,
)
from abren_one.modules.procurement.domain.value_objects import (
    AuthorizationStatus,
    PurchaseOrderStatus,
)

# ── Authorization transitions ─────────────────────────────────────────────

_VALID_AUTHORIZATION_TRANSITIONS: dict[AuthorizationStatus, set[AuthorizationStatus]] = {
    AuthorizationStatus.DRAFT: {AuthorizationStatus.SUBMITTED, AuthorizationStatus.CANCELLED},
    AuthorizationStatus.SUBMITTED: {
        AuthorizationStatus.APPROVED,
        AuthorizationStatus.REJECTED,
        AuthorizationStatus.DRAFT,  # return to draft
    },
    AuthorizationStatus.REJECTED: {AuthorizationStatus.DRAFT},  # revise
    AuthorizationStatus.APPROVED: set(),  # terminal for authorization
    AuthorizationStatus.CANCELLED: set(),  # terminal
}

_VALID_PO_TRANSITIONS: dict[PurchaseOrderStatus, set[PurchaseOrderStatus]] = {
    PurchaseOrderStatus.DRAFT: {PurchaseOrderStatus.ISSUED, PurchaseOrderStatus.CANCELLED},
    PurchaseOrderStatus.ISSUED: {PurchaseOrderStatus.CLOSED, PurchaseOrderStatus.CANCELLED},
    PurchaseOrderStatus.CLOSED: set(),
    PurchaseOrderStatus.CANCELLED: set(),
}


def validate_authorization_transition(current: str, target: str) -> None:
    """Validate a requisition authorization status transition."""
    curr = AuthorizationStatus(current)
    tgt = AuthorizationStatus(target)
    allowed = _VALID_AUTHORIZATION_TRANSITIONS.get(curr, set())
    if tgt not in allowed:
        raise InvalidRequisitionTransitionError(f"Cannot transition requisition from '{curr.value}' to '{tgt.value}'.")


def validate_po_transition(current: str, target: str) -> None:
    """Validate a purchase order status transition."""
    curr = PurchaseOrderStatus(current)
    tgt = PurchaseOrderStatus(target)
    allowed = _VALID_PO_TRANSITIONS.get(curr, set())
    if tgt not in allowed:
        raise InvalidPurchaseOrderTransitionError(
            f"Cannot transition purchase order from '{curr.value}' to '{tgt.value}'."
        )


# ── Segregation of duties ─────────────────────────────────────────────────


def validate_no_self_approval(requester_id: UUID, approver_id: UUID) -> None:
    """Prevent a requester from approving their own requisition."""
    if requester_id == approver_id:
        raise SelfApprovalError("A requisition cannot be approved by the person who requested it.")


# ── Vendor checks ─────────────────────────────────────────────────────────


def validate_vendor_active(is_active: bool) -> None:
    """Ensure vendor is active before creating commitments."""
    if not is_active:
        raise InactiveVendorError("Cannot create purchase orders for an inactive vendor.")


# ── Requisition integrity ─────────────────────────────────────────────────


def validate_requisition_has_items(item_count: int) -> None:
    """A requisition must have at least one item to be submitted."""
    if item_count < 1:
        raise EmptyRequisitionError("A purchase requisition must have at least one item.")


# ── Quantity reconciliation ───────────────────────────────────────────────


def validate_inspection_quantities(
    received: Decimal,
    accepted: Decimal,
    rejected: Decimal,
) -> None:
    """Enforce: accepted >= 0, rejected >= 0, accepted + rejected == received."""
    if accepted < 0:
        raise InspectionQuantityError("Accepted quantity cannot be negative.")
    if rejected < 0:
        raise InspectionQuantityError("Rejected quantity cannot be negative.")
    if accepted + rejected != received:
        raise InspectionQuantityError(
            f"Accepted ({accepted}) + rejected ({rejected}) must equal received ({received})."
        )


def validate_allocation_quantity(
    allocating: Decimal,
    requested: Decimal,
    already_allocated: Decimal,
) -> None:
    """Prevent over-allocation: already_allocated + allocating <= requested."""
    if allocating <= 0:
        raise OverAllocationError("Allocation quantity must be greater than zero.")
    if already_allocated + allocating > requested:
        raise OverAllocationError(
            f"Allocation of {allocating} would exceed requested quantity "
            f"({requested}). Already allocated: {already_allocated}."
        )


def validate_receipt_quantity(
    receiving: Decimal,
    ordered: Decimal,
    already_received: Decimal,
) -> None:
    """Warn-level check: flag over-receipt but do not block.

    Over-receipt is flagged but allowed because suppliers may deliver
    slightly more than ordered. The calling command should log a warning.
    """
    if receiving <= 0:
        raise OverReceiptError("Receipt quantity must be greater than zero.")
    total = already_received + receiving
    if total > ordered:
        # This is a warning condition, not a hard block.
        # The command should record this in audit metadata.
        pass


# ── PO cancellation ───────────────────────────────────────────────────────


def validate_po_can_cancel(has_accepted_receipts: bool) -> None:
    """Cannot cancel a PO after any GRN items have been accepted."""
    if has_accepted_receipts:
        raise CancellationBlockedError(
            "Cannot cancel a purchase order that has accepted goods receipts. Close the order instead."
        )
