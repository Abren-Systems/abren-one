"""Unit tests for Procurement domain policies and invariants."""

import uuid
from decimal import Decimal

import pytest

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
from abren_one.modules.procurement.domain.policies import (
    validate_allocation_quantity,
    validate_authorization_transition,
    validate_no_self_approval,
    validate_po_can_cancel,
    validate_po_transition,
    validate_receipt_quantity,
    validate_requisition_has_items,
    validate_vendor_active,
)
from abren_one.modules.procurement.domain.value_objects import (
    AuthorizationStatus,
    PurchaseOrderStatus,
    ReceiptType,
    VendorType,
    VendorVerificationStatus,
)


class TestValueObjects:
    def test_vendor_types(self):
        assert VendorType.GOODS == "goods"
        assert VendorType.SERVICES == "services"
        assert VendorType.CONSULTING == "consulting"

    def test_vendor_verification_statuses(self):
        assert VendorVerificationStatus.UNVERIFIED == "unverified"
        assert VendorVerificationStatus.VERIFIED == "verified"
        assert VendorVerificationStatus.SUSPENDED == "suspended"

    def test_authorization_statuses(self):
        assert AuthorizationStatus.DRAFT == "draft"
        assert AuthorizationStatus.SUBMITTED == "submitted"
        assert AuthorizationStatus.APPROVED == "approved"
        assert AuthorizationStatus.REJECTED == "rejected"
        assert AuthorizationStatus.CANCELLED == "cancelled"

    def test_po_statuses(self):
        assert PurchaseOrderStatus.DRAFT == "draft"
        assert PurchaseOrderStatus.ISSUED == "issued"
        assert PurchaseOrderStatus.CLOSED == "closed"
        assert PurchaseOrderStatus.CANCELLED == "cancelled"

    def test_receipt_types(self):
        assert ReceiptType.GOODS == "goods"
        assert ReceiptType.SERVICES == "services"


class TestAuthorizationTransitions:
    @pytest.mark.parametrize(
        ("curr", "tgt"),
        [
            ("draft", "submitted"),
            ("draft", "cancelled"),
            ("submitted", "approved"),
            ("submitted", "rejected"),
            ("submitted", "draft"),
            ("rejected", "draft"),
        ],
    )
    def test_valid_transitions(self, curr: str, tgt: str):
        validate_authorization_transition(curr, tgt)

    @pytest.mark.parametrize(
        ("curr", "tgt"),
        [
            ("draft", "approved"),
            ("draft", "rejected"),
            ("submitted", "cancelled"),
            ("approved", "draft"),
            ("approved", "cancelled"),
            ("rejected", "approved"),
            ("rejected", "cancelled"),
            ("cancelled", "draft"),
        ],
    )
    def test_invalid_transitions(self, curr: str, tgt: str):
        with pytest.raises(InvalidRequisitionTransitionError):
            validate_authorization_transition(curr, tgt)


class TestPurchaseOrderTransitions:
    @pytest.mark.parametrize(
        ("curr", "tgt"),
        [
            ("draft", "issued"),
            ("draft", "cancelled"),
            ("issued", "closed"),
            ("issued", "cancelled"),
        ],
    )
    def test_valid_transitions(self, curr: str, tgt: str):
        validate_po_transition(curr, tgt)

    @pytest.mark.parametrize(
        ("curr", "tgt"),
        [
            ("draft", "closed"),
            ("issued", "draft"),
            ("closed", "draft"),
            ("closed", "issued"),
            ("cancelled", "draft"),
            ("cancelled", "issued"),
        ],
    )
    def test_invalid_transitions(self, curr: str, tgt: str):
        with pytest.raises(InvalidPurchaseOrderTransitionError):
            validate_po_transition(curr, tgt)


class TestSegregationOfDuties:
    def test_different_users_allowed(self):
        requester = uuid.uuid4()
        approver = uuid.uuid4()
        validate_no_self_approval(requester, approver)

    def test_same_user_raises_error(self):
        user = uuid.uuid4()
        with pytest.raises(SelfApprovalError, match="cannot be approved by the person who requested it"):
            validate_no_self_approval(user, user)


class TestVendorActiveValidation:
    def test_active_vendor_allowed(self):
        validate_vendor_active(True)

    def test_inactive_vendor_raises_error(self):
        with pytest.raises(InactiveVendorError, match="inactive vendor"):
            validate_vendor_active(False)


class TestRequisitionItemsValidation:
    def test_has_items_allowed(self):
        validate_requisition_has_items(1)
        validate_requisition_has_items(5)

    def test_zero_items_raises_error(self):
        with pytest.raises(EmptyRequisitionError, match="must have at least one item"):
            validate_requisition_has_items(0)


class TestInspectionQuantitiesValidation:
    def test_exact_reconciliation_allowed(self):
        from abren_one.modules.procurement.domain.policies import validate_inspection_quantities

        validate_inspection_quantities(Decimal("10"), Decimal("8"), Decimal("2"))
        validate_inspection_quantities(Decimal("10"), Decimal("10"), Decimal("0"))
        validate_inspection_quantities(Decimal("10"), Decimal("0"), Decimal("10"))

    def test_negative_accepted_raises_error(self):
        from abren_one.modules.procurement.domain.policies import validate_inspection_quantities

        with pytest.raises(InspectionQuantityError, match="Accepted quantity cannot be negative"):
            validate_inspection_quantities(Decimal("10"), Decimal("-1"), Decimal("11"))

    def test_negative_rejected_raises_error(self):
        from abren_one.modules.procurement.domain.policies import validate_inspection_quantities

        with pytest.raises(InspectionQuantityError, match="Rejected quantity cannot be negative"):
            validate_inspection_quantities(Decimal("10"), Decimal("11"), Decimal("-1"))

    def test_unreconciled_sum_raises_error(self):
        from abren_one.modules.procurement.domain.policies import validate_inspection_quantities

        with pytest.raises(InspectionQuantityError, match="must equal received"):
            validate_inspection_quantities(Decimal("10"), Decimal("7"), Decimal("2"))


class TestAllocationQuantityValidation:
    def test_valid_allocation(self):
        validate_allocation_quantity(Decimal("5"), Decimal("10"), Decimal("3"))
        validate_allocation_quantity(Decimal("7"), Decimal("10"), Decimal("3"))

    def test_zero_or_negative_allocation_raises_error(self):
        with pytest.raises(OverAllocationError, match="greater than zero"):
            validate_allocation_quantity(Decimal("0"), Decimal("10"), Decimal("0"))
        with pytest.raises(OverAllocationError, match="greater than zero"):
            validate_allocation_quantity(Decimal("-1"), Decimal("10"), Decimal("0"))

    def test_over_allocation_raises_error(self):
        with pytest.raises(OverAllocationError, match="would exceed requested quantity"):
            validate_allocation_quantity(Decimal("8"), Decimal("10"), Decimal("3"))


class TestReceiptQuantityValidation:
    def test_normal_receipt_allowed(self):
        validate_receipt_quantity(Decimal("5"), Decimal("10"), Decimal("3"))

    def test_zero_or_negative_receipt_raises_error(self):
        with pytest.raises(OverReceiptError, match="greater than zero"):
            validate_receipt_quantity(Decimal("0"), Decimal("10"), Decimal("0"))

    def test_over_receipt_logs_warning_without_exception(self):
        # Over-receipt is a warning condition, not a hard block
        validate_receipt_quantity(Decimal("10"), Decimal("10"), Decimal("5"))


class TestPurchaseOrderCancellationValidation:
    def test_can_cancel_without_accepted_receipts(self):
        validate_po_can_cancel(has_accepted_receipts=False)

    def test_cannot_cancel_with_accepted_receipts(self):
        with pytest.raises(CancellationBlockedError, match="has accepted goods receipts"):
            validate_po_can_cancel(has_accepted_receipts=True)
