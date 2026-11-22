from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.finance.domain.exceptions import (
    AccountNotFoundError,
    FinanceDomainError,
)
from abren_one.modules.finance.models import Account
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class AccountDetailResult:
    id: UUID
    organization_id: UUID
    code: str
    name: str
    account_type: str
    currency: str
    is_active: bool
    description: str
    parent_id: UUID | None


def execute(account_id: UUID, context: ExecutionContext) -> AccountDetailResult:
    """Retrieve full details of an account by ID (§6.2)."""
    if context.organization_id is None:
        raise FinanceDomainError("Organization context is required.")

    try:
        acc = Account.objects.get(id=account_id, organization_id=context.organization_id)
    except Account.DoesNotExist as exc:
        raise AccountNotFoundError("Account not found in this organization.") from exc

    return AccountDetailResult(
        id=acc.id,
        organization_id=acc.organization_id,
        code=acc.code,
        name=acc.name,
        account_type=acc.account_type,
        currency=acc.currency,
        is_active=acc.is_active,
        description=acc.description,
        parent_id=acc.parent_id,
    )
