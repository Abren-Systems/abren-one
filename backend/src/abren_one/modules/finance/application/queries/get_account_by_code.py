"""Query to retrieve an account by its code within an organization."""

from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.finance.domain.exceptions import (
    AccountNotFoundError,
    FinanceDomainError,
)
from abren_one.modules.finance.models import Account


@dataclass(frozen=True)
class AccountByCodeResult:
    id: UUID
    code: str
    name: str
    account_type: str
    currency: str
    is_active: bool


def execute(
    organization_id: UUID,
    account_code: str,
) -> AccountByCodeResult:
    """Look up an account by its code within an organization.

    Used by cross-module bridges to resolve standard GL account codes
    (e.g., "1200" for Inventory Asset) into account IDs for journal entries.
    """
    if organization_id is None:
        raise FinanceDomainError("Organization context is required.")

    try:
        acc = Account.objects.get(
            organization_id=organization_id,
            code=account_code,
        )
    except Account.DoesNotExist as exc:
        raise AccountNotFoundError(f"Account with code '{account_code}' not found in this organization.") from exc

    return AccountByCodeResult(
        id=acc.id,
        code=acc.code,
        name=acc.name,
        account_type=acc.account_type,
        currency=acc.currency,
        is_active=acc.is_active,
    )
