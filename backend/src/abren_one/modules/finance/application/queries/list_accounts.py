from dataclasses import dataclass
from uuid import UUID

from abren_one.modules.finance.domain.exceptions import FinanceDomainError
from abren_one.modules.finance.models import Account
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class AccountSummaryResult:
    id: UUID
    code: str
    name: str
    account_type: str
    currency: str
    is_active: bool


def execute(
    context: ExecutionContext,
    account_type: str | None = None,
    is_active: bool | None = None,
) -> list[AccountSummaryResult]:
    """List all accounts for the active organization (§6.2)."""
    if context.organization_id is None:
        raise FinanceDomainError("Organization context is required.")

    qs = Account.objects.filter(organization_id=context.organization_id)
    if account_type:
        qs = qs.filter(account_type=account_type)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)

    return [
        AccountSummaryResult(
            id=acc.id,
            code=acc.code,
            name=acc.name,
            account_type=acc.account_type,
            currency=acc.currency,
            is_active=acc.is_active,
        )
        for acc in qs
    ]
