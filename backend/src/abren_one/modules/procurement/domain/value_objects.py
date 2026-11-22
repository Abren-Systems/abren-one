"""Value objects and enumerations for the Procurement domain."""

from enum import StrEnum


class VendorType(StrEnum):
    """Classification of supplier type."""

    GOODS = "goods"
    SERVICES = "services"
    CONSULTING = "consulting"


class VendorVerificationStatus(StrEnum):
    """Verification lifecycle for a vendor."""

    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    SUSPENDED = "suspended"


class AuthorizationStatus(StrEnum):
    """Authorization lifecycle for procurement requests.

    Fulfillment position (ordered/received/outstanding) is derived from
    allocation and receipt quantities — never stored as a status enum.
    """

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class PurchaseOrderStatus(StrEnum):
    """Lifecycle states of a purchase order.

    Delivery position is derived from GRN data — not stored as status.
    """

    DRAFT = "draft"
    ISSUED = "issued"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class ReceiptType(StrEnum):
    """Distinguishes goods delivery from service completion."""

    GOODS = "goods"
    SERVICES = "services"
