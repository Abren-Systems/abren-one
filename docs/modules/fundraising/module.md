# Fundraising Module

**App label:** `fundraising`  
**Location:** `backend/src/abren_one/modules/fundraising/`  
**Status:** Implemented

---

## Purpose

Manages donor engagement, institutional grants, and monetary contributions (donations). It provides NGOs with a structured, auditable domain for managing funding streams and linking resources to strategic programs.

---

## Owned Models

| Model | Description |
|-------|-------------|
| `Donor` | An individual or institutional supporter (corporation, foundation, government agency). |
| `Grant` | An institutional funding agreement with defined start/end dates, total funding amount, and status lifecycle. |
| `Donation` | A specific monetary contribution received, recording amount, currency, payment method, and optional links to a grant or program. |

All models inherit [`OrgOwnedMixin`](file:///Users/yuma/djprojects/abren-one/backend/src/abren_one/platform/common/models/__init__.py) and [`TimestampMixin`](file:///Users/yuma/djprojects/abren-one/backend/src/abren_one/platform/common/models/__init__.py).

---

## Public Interface

**File:** `public.py`

Other modules import **only** from this file.

### Public Exports

| Export | Type | Description |
|--------|------|-------------|
| `create_donor` | Command | Create a donor record for the active organization. |
| `create_grant` | Command | Create an institutional grant agreement. |
| `record_donation` | Command | Record a monetary donation with audit persistence. |
| `get_donor` | Query | Retrieve donor details. |
| `list_donors` | Query | List donors in the active organization. |
| `get_grant` | Query | Retrieve grant details. |
| `list_grants` | Query | List grants in the active organization. |
| `list_donations` | Query | List donations in the active organization. |
| `CreateDonorInput` / `Result` | DTO | Input / output dataclasses for donor creation. |
| `CreateGrantInput` / `Result` | DTO | Input / output dataclasses for grant creation. |
| `RecordDonationInput` / `Result` | DTO | Input / output dataclasses for recording donations. |
| `GetDonorResult` / `DonorSummaryResult` | DTO | Query result dataclasses for donors. |
| `GetGrantResult` / `GrantSummaryResult` | DTO | Query result dataclasses for grants. |
| `DonationSummaryResult` | DTO | Query result dataclass for donations. |
| `FundraisingError` | Exception | Base domain exception for fundraising. |
| `DonorNotFoundError` | Exception | Raised when donor is not found. |
| `GrantNotFoundError` | Exception | Raised when grant is not found. |
| `DonationNotFoundError` | Exception | Raised when donation is not found. |
| `InactiveDonorError` | Exception | Raised when donor is inactive. |
| `InvalidDonationAmountError` | Exception | Raised when donation amount is non-positive. |
| `GrantMismatchError` | Exception | Raised when grant donor mismatches donation donor. |

---

## Cross-Module Interactions

1. **Organizations:** Every operation validates organization status via `from abren_one.modules.organizations.public import get_organization`.
2. **Programs:** When grants or donations link to a program (`program_id`), validity is checked via `from abren_one.modules.programs.public import get_program`.
3. **Audit:** Every command records an audit event via `record_audit_event`.

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| `GET` | `/api/v1/fundraising/donors/` | List donors for active organization. |
| `POST` | `/api/v1/fundraising/donors/` | Create a new donor. |
| `GET` | `/api/v1/fundraising/donors/{id}/` | Retrieve donor detail. |
| `GET` | `/api/v1/fundraising/grants/` | List grants for active organization. |
| `POST` | `/api/v1/fundraising/grants/` | Create a grant agreement. |
| `GET` | `/api/v1/fundraising/grants/{id}/` | Retrieve grant detail. |
| `GET` | `/api/v1/fundraising/donations/` | List donations for active organization. |
| `POST` | `/api/v1/fundraising/donations/` | Record a donation. |
