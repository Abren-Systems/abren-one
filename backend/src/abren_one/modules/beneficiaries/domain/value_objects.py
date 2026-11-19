from enum import StrEnum


class BeneficiaryType(StrEnum):
    INDIVIDUAL = "individual"
    HOUSEHOLD = "household"
    COMMUNITY = "community"


class BeneficiaryStatus(StrEnum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    GRADUATED = "graduated"
    ARCHIVED = "archived"


class VulnerabilityLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ServiceType(StrEnum):
    FOOD_ASSISTANCE = "food_assistance"
    MEDICAL_SUPPORT = "medical_support"
    CASH_TRANSFER = "cash_transfer"
    EDUCATION_TRAINING = "education_training"
    SHELTER_WASH = "shelter_wash"
    LEGAL_ADVOCACY = "legal_advocacy"
    OTHER = "other"


class DeliveryStatus(StrEnum):
    PLANNED = "planned"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Gender(StrEnum):
    FEMALE = "female"
    MALE = "male"
    UNSPECIFIED = "unspecified"
