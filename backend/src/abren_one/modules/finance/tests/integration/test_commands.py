import uuid
from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError

from abren_one.modules.finance.domain.exceptions import (
    AccountNotFoundError,
    FinanceDomainError,
    ImmutableJournalEntryError,
    UnbalancedJournalEntryError,
)
from abren_one.modules.finance.models import JournalEntry, JournalLine
from abren_one.modules.finance.public import (
    AccountType,
    CreateAccountInput,
    CreateJournalEntryInput,
    JournalEntryStatus,
    JournalLineInput,
    PostJournalEntryInput,
    ReverseJournalEntryInput,
    create_account,
    create_journal_entry,
    get_account,
    get_account_by_code,
    get_journal_entry,
    get_trial_balance,
    post_journal_entry,
    reverse_journal_entry,
)
from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.platform.audit.models import AuditEvent
from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.fixture
def org_context() -> tuple[uuid.UUID, ExecutionContext]:
    actor_id = uuid.uuid4()
    corr_id = uuid.uuid4()
    init_ctx = ExecutionContext(
        actor_type=ActorType.SYSTEM,
        actor_id=None,
        organization_id=None,
        correlation_id=corr_id,
    )
    org_res = create_organization(
        CreateOrganizationInput(
            context=init_ctx,
            name="Emergency Relief NGO",
            slug="emergency-relief-ngo",
        )
    )
    ctx = ExecutionContext(
        actor_type=ActorType.USER,
        actor_id=actor_id,
        organization_id=org_res.organization_id,
        correlation_id=corr_id,
        actor_role="admin",
    )
    return org_res.organization_id, ctx


@pytest.mark.django_db
class TestAccountCommands:
    def test_create_account_success(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        res = create_account(
            CreateAccountInput(
                context=ctx,
                code="1010",
                name="Operating Cash",
                account_type=AccountType.ASSET.value,
                currency="USD",
            )
        )
        assert res.code == "1010"
        assert res.account_type == "asset"

        # Verify query
        acc = get_account(res.account_id, ctx)
        assert acc.code == "1010"
        assert acc.name == "Operating Cash"

        # Verify audit event
        assert AuditEvent.objects.filter(action="finance.account.created", target_id=res.account_id).exists()

    def test_reject_duplicate_account_code(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        create_account(
            CreateAccountInput(
                context=ctx,
                code="1010",
                name="Cash Account",
                account_type=AccountType.ASSET.value,
            )
        )
        with pytest.raises(FinanceDomainError, match="already exists"):
            create_account(
                CreateAccountInput(
                    context=ctx,
                    code="1010",
                    name="Duplicate Cash",
                    account_type=AccountType.ASSET.value,
                )
            )


@pytest.mark.django_db
class TestJournalEntryLifecycle:
    def test_draft_post_and_trial_balance(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context

        # 1. Create accounts
        cash = create_account(
            CreateAccountInput(
                context=ctx,
                code="1010",
                name="Operating Cash",
                account_type=AccountType.ASSET.value,
            )
        )
        donations = create_account(
            CreateAccountInput(
                context=ctx,
                code="4010",
                name="Donation Revenue",
                account_type=AccountType.REVENUE.value,
            )
        )

        # 2. Create balanced draft entry
        je_res = create_journal_entry(
            CreateJournalEntryInput(
                context=ctx,
                entry_date=date(2026, 11, 22),
                memo="Initial donor grant funding",
                currency="USD",
                lines=[
                    JournalLineInput(
                        account_id=cash.account_id,
                        debit=Decimal("25000.00"),
                        credit=Decimal("0.00"),
                    ),
                    JournalLineInput(
                        account_id=donations.account_id,
                        debit=Decimal("0.00"),
                        credit=Decimal("25000.00"),
                    ),
                ],
                post_immediately=False,
            )
        )
        assert je_res.status == JournalEntryStatus.DRAFT.value
        assert je_res.total_debits == Decimal("25000.00")
        assert je_res.total_credits == Decimal("25000.00")

        # 3. Before posting, Trial Balance has no posted entries
        tb_before = get_trial_balance(ctx)
        assert tb_before.total_debits == Decimal("0.00")
        assert tb_before.total_credits == Decimal("0.00")

        # 4. Post journal entry
        post_res = post_journal_entry(
            PostJournalEntryInput(
                context=ctx,
                journal_entry_id=je_res.journal_entry_id,
            )
        )
        assert post_res.status == JournalEntryStatus.POSTED.value

        # Verify entry details
        entry = get_journal_entry(je_res.journal_entry_id, ctx)
        assert entry.status == JournalEntryStatus.POSTED.value
        assert len(entry.lines) == 2

        # 5. After posting, Trial Balance reflects the balances and is balanced
        tb_after = get_trial_balance(ctx)
        assert tb_after.is_balanced is True
        assert tb_after.total_debits == Decimal("25000.00")
        assert tb_after.total_credits == Decimal("25000.00")

        # Verify audit trail
        assert AuditEvent.objects.filter(
            action="finance.journal_entry.posted",
            target_id=je_res.journal_entry_id,
        ).exists()

    def test_reject_unbalanced_journal_entry(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        cash = create_account(
            CreateAccountInput(
                context=ctx,
                code="1010",
                name="Cash",
                account_type=AccountType.ASSET.value,
            )
        )
        donations = create_account(
            CreateAccountInput(
                context=ctx,
                code="4010",
                name="Donations",
                account_type=AccountType.REVENUE.value,
            )
        )

        with pytest.raises(UnbalancedJournalEntryError, match="unbalanced"):
            create_journal_entry(
                CreateJournalEntryInput(
                    context=ctx,
                    entry_date=date(2026, 11, 22),
                    memo="Faulty unbalanced entry",
                    lines=[
                        JournalLineInput(
                            account_id=cash.account_id,
                            debit=Decimal("1000.00"),
                            credit=Decimal("0.00"),
                        ),
                        JournalLineInput(
                            account_id=donations.account_id,
                            debit=Decimal("0.00"),
                            credit=Decimal("500.00"),
                        ),
                    ],
                )
            )

    def test_reverse_journal_entry(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        cash = create_account(
            CreateAccountInput(
                context=ctx,
                code="1010",
                name="Cash",
                account_type=AccountType.ASSET.value,
            )
        )
        expense = create_account(
            CreateAccountInput(
                context=ctx,
                code="5010",
                name="Supplies Expense",
                account_type=AccountType.EXPENSE.value,
            )
        )

        # Create & post entry
        je_res = create_journal_entry(
            CreateJournalEntryInput(
                context=ctx,
                entry_date=date(2026, 11, 22),
                memo="Incorrect supplies purchase",
                lines=[
                    JournalLineInput(account_id=expense.account_id, debit=Decimal("1200.00")),
                    JournalLineInput(account_id=cash.account_id, credit=Decimal("1200.00")),
                ],
                post_immediately=True,
            )
        )

        # Reverse the posted entry
        rev_res = reverse_journal_entry(
            ReverseJournalEntryInput(
                context=ctx,
                journal_entry_id=je_res.journal_entry_id,
                reason="Vendor refunded invoice",
            )
        )
        assert rev_res.reversal_entry_number.startswith("REV-")

        # Verify original entry is marked REVERSED
        orig = get_journal_entry(je_res.journal_entry_id, ctx)
        assert orig.status == JournalEntryStatus.REVERSED.value

        # Verify reversal entry is POSTED with inverted debits and credits
        rev = get_journal_entry(rev_res.reversal_entry_id, ctx)
        assert rev.status == JournalEntryStatus.POSTED.value
        assert rev.reversal_of_id == orig.id

        # Trial balance should net out to zero
        tb = get_trial_balance(ctx)
        assert tb.is_balanced is True
        assert tb.total_debits == Decimal("0.00")
        assert tb.total_credits == Decimal("0.00")

    def test_cannot_reverse_already_reversed_entry(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        _, ctx = org_context
        cash = create_account(CreateAccountInput(context=ctx, code="1010", name="Cash"))
        rev_acc = create_account(CreateAccountInput(context=ctx, code="4010", name="Donations", account_type="revenue"))

        je_res = create_journal_entry(
            CreateJournalEntryInput(
                context=ctx,
                entry_date=date(2026, 11, 22),
                memo="Entry to reverse twice",
                lines=[
                    JournalLineInput(account_id=cash.account_id, debit=Decimal("100.00")),
                    JournalLineInput(account_id=rev_acc.account_id, credit=Decimal("100.00")),
                ],
                post_immediately=True,
            )
        )

        reverse_journal_entry(
            ReverseJournalEntryInput(
                context=ctx,
                journal_entry_id=je_res.journal_entry_id,
                reason="First reversal",
            )
        )

        with pytest.raises(ImmutableJournalEntryError, match="Only posted journal entries can be reversed"):
            reverse_journal_entry(
                ReverseJournalEntryInput(
                    context=ctx,
                    journal_entry_id=je_res.journal_entry_id,
                    reason="Second reversal attempt",
                )
            )


@pytest.mark.django_db
class TestDatabaseConstraints:
    def test_check_constraint_rejects_line_with_both_debit_and_credit(
        self,
        org_context: tuple[uuid.UUID, ExecutionContext],
    ):
        org_id, ctx = org_context
        acc = create_account(CreateAccountInput(context=ctx, code="1010", name="Cash"))
        entry_res = create_journal_entry(
            CreateJournalEntryInput(
                context=ctx,
                entry_date=date(2026, 11, 22),
                memo="Valid entry",
                lines=[
                    JournalLineInput(account_id=acc.account_id, debit=Decimal("50.00")),
                    JournalLineInput(account_id=acc.account_id, credit=Decimal("50.00")),
                ],
            )
        )

        with pytest.raises(IntegrityError):
            JournalLine.objects.create(
                journal_entry_id=entry_res.journal_entry_id,
                account_id=acc.account_id,
                debit=Decimal("10.00"),
                credit=Decimal("10.00"),  # Violates finance_line_debit_xor_credit constraint
            )

    def test_posted_journal_entry_and_lines_are_immutable(
        self,
        org_context: tuple[uuid.UUID, ExecutionContext],
    ):
        org_id, ctx = org_context
        cash = create_account(CreateAccountInput(context=ctx, code="1010", name="Cash"))
        rev = create_account(CreateAccountInput(context=ctx, code="4010", name="Revenue", account_type="revenue"))

        entry_res = create_journal_entry(
            CreateJournalEntryInput(
                context=ctx,
                entry_date=date(2026, 11, 22),
                memo="Posted entry",
                lines=[
                    JournalLineInput(account_id=cash.account_id, debit=Decimal("200.00")),
                    JournalLineInput(account_id=rev.account_id, credit=Decimal("200.00")),
                ],
                post_immediately=True,
            )
        )
        entry = JournalEntry.objects.get(id=entry_res.journal_entry_id)
        line = entry.lines.first()
        assert line is not None

        # Cannot delete posted entry
        with pytest.raises(ImmutableJournalEntryError, match="cannot be deleted"):
            entry.delete()

        # Cannot modify posted entry fields
        entry.memo = "Tampered memo"
        with pytest.raises(ImmutableJournalEntryError, match="cannot be modified"):
            entry.save()

        # Cannot delete or modify lines belonging to posted entry
        with pytest.raises(ImmutableJournalEntryError, match="cannot be deleted"):
            line.delete()

        line.memo = "Tampered line memo"
        with pytest.raises(ImmutableJournalEntryError, match="cannot be modified"):
            line.save()

    def test_soft_reference_validation_rejects_foreign_tenant_or_nonexistent_ids(
        self,
        org_context: tuple[uuid.UUID, ExecutionContext],
    ):
        org_id, ctx = org_context
        cash = create_account(CreateAccountInput(context=ctx, code="1010", name="Cash"))
        rev = create_account(CreateAccountInput(context=ctx, code="4010", name="Revenue", account_type="revenue"))

        fake_program_id = uuid.uuid4()
        with pytest.raises(FinanceDomainError, match=f"Program {fake_program_id} not found"):
            create_journal_entry(
                CreateJournalEntryInput(
                    context=ctx,
                    entry_date=date(2026, 11, 22),
                    memo="Invalid program reference",
                    lines=[
                        JournalLineInput(account_id=cash.account_id, debit=Decimal("100.00")),
                        JournalLineInput(account_id=rev.account_id, credit=Decimal("100.00")),
                    ],
                    program_id=fake_program_id,
                )
            )

    def test_permission_denial_for_member_role(
        self,
        org_context: tuple[uuid.UUID, ExecutionContext],
    ):
        from django.core.exceptions import PermissionDenied

        org_id, _ = org_context
        member_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org_id,
            correlation_id=uuid.uuid4(),
            actor_role="member",
        )

        with pytest.raises(PermissionDenied, match="Permission 'finance:accounts:manage' denied"):
            create_account(
                CreateAccountInput(
                    context=member_ctx,
                    code="9999",
                    name="Unauthorized Account",
                )
            )


@pytest.mark.django_db
class TestGetAccountByCode:
    def test_get_account_by_code_success(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        org_id, ctx = org_context
        created = create_account(
            CreateAccountInput(
                context=ctx,
                code="1200",
                name="Inventory Asset",
                account_type=AccountType.ASSET.value,
                currency="USD",
            )
        )
        res = get_account_by_code(org_id, "1200")
        assert res.id == created.account_id
        assert res.code == "1200"
        assert res.name == "Inventory Asset"
        assert res.account_type == "asset"
        assert res.currency == "USD"
        assert res.is_active is True

    def test_get_account_by_code_not_found(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        org_id, _ = org_context
        with pytest.raises(AccountNotFoundError, match="Account with code '9999' not found"):
            get_account_by_code(org_id, "9999")

    def test_get_account_by_code_tenant_isolated(self, org_context: tuple[uuid.UUID, ExecutionContext]):
        org_a_id, ctx_a = org_context
        create_account(
            CreateAccountInput(
                context=ctx_a,
                code="1200",
                name="Org A Inventory",
                account_type=AccountType.ASSET.value,
            )
        )
        # Create Org B
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org_b_res = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Other Organization",
                slug=f"other-{uuid.uuid4().hex[:6]}",
            )
        )
        org_b_id = org_b_res.organization_id

        # Querying Org B for code '1200' must raise AccountNotFoundError
        with pytest.raises(AccountNotFoundError):
            get_account_by_code(org_b_id, "1200")
