from dataclasses import dataclass
from uuid import UUID

from django.db import transaction

from abren_one.modules.finance.domain.exceptions import (
    FinanceDomainError,
    InvalidAccountTypeError,
)
from abren_one.modules.finance.domain.value_objects import AccountType
from abren_one.modules.finance.models import Account
from abren_one.modules.organizations.public import get_organization
from abren_one.platform.audit.service import record_audit_event
from abren_one.platform.common.context import ExecutionContext


@dataclass(frozen=True)
class CreateAccountInput:
    context: ExecutionContext
    code: str
    name: str
    account_type: str = AccountType.ASSET.value
    currency: str = "USD"
    description: str = ""
    parent_id: UUID | None = None


@dataclass(frozen=True)
class CreateAccountResult:
    account_id: UUID
    code: str
    name: str
    account_type: str
    currency: str


@transaction.atomic
def execute(data: CreateAccountInput) -> CreateAccountResult:
    """Create a new account in the Chart of Accounts (§6.2)."""
    if data.context.organization_id is None:
        raise FinanceDomainError("Organization context is required.")

    org = get_organization(organization_id=data.context.organization_id)
    if not org.is_active:
        raise FinanceDomainError("Cannot create account for an inactive or suspended organization.")

    valid_types = {t.value for t in AccountType}
    if data.account_type not in valid_types:
        raise InvalidAccountTypeError(
            f"Invalid account type '{data.account_type}'. Must be one of {sorted(valid_types)}."
        )

    code = data.code.strip()
    if not code:
        raise FinanceDomainError("Account code cannot be empty.")

    name = data.name.strip()
    if not name:
        raise FinanceDomainError("Account name cannot be empty.")

    if Account.objects.filter(organization_id=org.id, code=code).exists():
        raise FinanceDomainError(f"Account with code '{code}' already exists in this organization.")

    parent = None
    if data.parent_id:
        try:
            parent = Account.objects.get(id=data.parent_id, organization_id=org.id)
        except Account.DoesNotExist as exc:
            raise FinanceDomainError("Parent account not found in this organization.") from exc

    account = Account.objects.create(
        organization_id=org.id,
        code=code,
        name=name,
        account_type=data.account_type,
        currency=data.currency.upper(),
        description=data.description.strip(),
        parent=parent,
    )

    record_audit_event(
        actor_type=data.context.actor_type.value,
        actor_id=data.context.actor_id,
        organization_id=org.id,
        action="finance.account.created",
        target_type="finance.Account",
        target_id=account.id,
        correlation_id=data.context.correlation_id,
        metadata={"code": account.code, "name": account.name, "account_type": account.account_type},
    )

    return CreateAccountResult(
        account_id=account.id,
        code=account.code,
        name=account.name,
        account_type=account.account_type,
        currency=account.currency,
    )
