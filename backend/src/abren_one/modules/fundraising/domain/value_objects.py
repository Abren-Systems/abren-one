from enum import StrEnum


class DonorType(StrEnum):
    INDIVIDUAL = "individual"
    CORPORATE = "corporate"
    FOUNDATION = "foundation"
    GOVERNMENT = "government"


class DonorStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class GrantStatus(StrEnum):
    PROPOSED = "proposed"
    AWARDED = "awarded"
    ACTIVE = "active"
    COMPLETED = "completed"
    CLOSED = "closed"


class DonationStatus(StrEnum):
    RECEIVED = "received"
    CONFIRMED = "confirmed"
    REFUNDED = "refunded"


class PaymentMethod(StrEnum):
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    ONLINE = "online"
    CASH = "cash"
    OTHER = "other"
