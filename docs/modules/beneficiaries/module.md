# Beneficiaries Module

**App label:** `beneficiaries`  
**Location:** `backend/src/abren_one/modules/beneficiaries/`  
**Status:** Implemented  

---

## Purpose

Manages beneficiary records and service delivery tracking. It provides NGOs with a structured, auditable domain for identifying who receives support (individuals, households, communities), their vulnerability profiles, and tracking discrete assistance events (food, medical, cash transfers, education, etc.) linked to organizational programs and activities.

---

## Owned Models

| Model | Description |
|-------|-------------|
| `Beneficiary` | An individual, household, or community receiving aid, including contact info, vulnerability rating, and lifecycle status. |
| `ServiceDelivery` | A specific instance of assistance or service delivered to a beneficiary, recording quantity, service type, delivery status, and optional soft references to program/activity. |

All models inherit [`OrgOwnedMixin`](file:///Users/yuma/djprojects/abren-one/backend/src/abren_one/platform/common/models/__init__.py) and [`TimestampMixin`](file:///Users/yuma/djprojects/abren-one/backend/src/abren_one/platform/common/models/__init__.py).

---

## Public Interface

**File:** `public.py`

Other modules import **only** from this file.

### Public Exports

| Export | Type | Description |
|--------|------|-------------|
| `register_beneficiary` | Command | Register a beneficiary (individual/household/community) in the active organization. |
| `update_beneficiary` | Command | Update beneficiary attributes or transition lifecycle status. |
| `record_service_delivery` | Command | Record an assistance delivery to an active beneficiary with audit persistence. |
| `get_beneficiary` | Query | Retrieve full beneficiary details. |
| `list_beneficiaries` | Query | List beneficiaries in the active organization, with optional status/type filtering. |
| `get_service_delivery` | Query | Retrieve service delivery details. |
| `list_service_deliveries` | Query | List service deliveries for the active organization, optionally filtered by beneficiary. |
| `RegisterBeneficiaryInput` / `Result` | DTO | Input / output dataclasses for beneficiary registration. |
| `UpdateBeneficiaryInput` / `Result` | DTO | Input / output dataclasses for updating beneficiary records. |
| `RecordServiceDeliveryInput` / `Result` | DTO | Input / output dataclasses for recording service deliveries. |
| `GetBeneficiaryResult` / `BeneficiarySummaryResult` | DTO | Query result dataclasses for beneficiaries. |
| `GetServiceDeliveryResult` / `ServiceDeliverySummaryResult` | DTO | Query result dataclasses for service deliveries. |
| `BeneficiaryError` | Exception | Base domain exception for beneficiaries. |
| `BeneficiaryNotFoundError` | Exception | Raised when beneficiary is not found. |
| `InactiveBeneficiaryError` | Exception | Raised when attempting delivery to a non-active beneficiary. |
| `InvalidBeneficiaryTransitionError` | Exception | Raised when a beneficiary status transition is not permitted by policy. |
| `InvalidDeliveryTransitionError` | Exception | Raised when a delivery status transition is not permitted by policy. |
| `ServiceDeliveryNotFoundError` | Exception | Raised when service delivery record is not found. |

---

## Cross-Module Interactions

1. **Organizations:** Every operation validates organization status via `from abren_one.modules.organizations.public import get_organization`.
2. **Programs:** When service deliveries link to a program (`program_id`) or activity (`activity_id`), validity is checked via:
   - `from abren_one.modules.programs.public import get_program`
   - `from abren_one.modules.programs.public import get_activity`
3. **Audit:** Every command records an audit event via `record_audit_event`.

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/v1/beneficiaries/` | List beneficiaries for active organization. |
| `POST` | `/api/v1/beneficiaries/` | Register a new beneficiary. |
| `GET` | `/api/v1/beneficiaries/{id}/` | Retrieve beneficiary details. |
| `PATCH` | `/api/v1/beneficiaries/{id}/` | Update beneficiary profile or lifecycle status. |
| `GET` | `/api/v1/beneficiaries/deliveries/` | List service deliveries for active organization. |
| `POST` | `/api/v1/beneficiaries/deliveries/` | Record a new service delivery. |
| `GET` | `/api/v1/beneficiaries/deliveries/{id}/` | Retrieve service delivery details. |
