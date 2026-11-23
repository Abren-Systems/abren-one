"""Integration tests for Fundraising → Finance GL Bridge (ADR-006).

Verifies that monetary donations automatically post balanced journal entries
to the General Ledger (Dr 1010 Cash/Bank, Cr 3100 Restricted Revenue) when
accounts exist, and gracefully degrade when accounts are not configured.
"""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from abren_one.modules.finance.public import (
    AccountType,
    CreateAccountInput,
    JournalEntryStatus,
    create_account,
    get_journal_entry,
    list_journal_entries,
)
from abren_one.modules.fundraising.application.commands.activate_grant import (
    ActivateGrantInput,
)
from abren_one.modules.fundraising.application.commands.activate_grant import (
    execute as activate_grant,
)
from abren_one.modules.fundraising.application.commands.award_grant import (
    AwardGrantInput,
)
from abren_one.modules.fundraising.application.commands.award_grant import (
    execute as award_grant,
)
from abren_one.modules.fundraising.application.commands.create_donor import (
    CreateDonorInput,
)
from abren_one.modules.fundraising.application.commands.create_donor import (
    execute as create_donor,
)
from abren_one.modules.fundraising.application.commands.create_grant import (
    CreateGrantInput,
)
from abren_one.modules.fundraising.application.commands.create_grant import (
    execute as create_grant,
)
from abren_one.modules.fundraising.application.commands.record_donation import (
    RecordDonationInput,
)
from abren_one.modules.fundraising.application.commands.record_donation import (
    execute as record_donation,
)
from abren_one.modules.fundraising.domain.value_objects import (
    DonorType,
    PaymentMethod,
)
from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.platform.authorization.roles import Role
from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.mark.django_db
class TestFundraisingToFinanceGLBridge:
    @pytest.fixture(autouse=True)
    def setup_fixtures(self) -> None:
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid4(),
        )
        org_res = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Hope Worldwide Relief",
                slug=f"hwr-{uuid4().hex[:6]}",
            )
        )
        self.org_id = org_res.organization_id

        self.admin_ctx = ExecutionContext(
            organization_id=self.org_id,
            actor_type=ActorType.USER,
            actor_id=uuid4(),
            actor_role=Role.ADMIN.value,
            correlation_id=uuid4(),
        )

        # 1. Setup Standard GL Accounts (1010 Cash/Bank, 3100 Restricted Revenue)
        self.acc_cash = create_account(
            CreateAccountInput(
                context=self.admin_ctx,
                code="1010",
                name="Operating Cash and Bank",
                account_type=AccountType.ASSET.value,
                currency="USD",
            )
        )
        self.acc_revenue = create_account(
            CreateAccountInput(
                context=self.admin_ctx,
                code="3100",
                name="Donor Revenue - Temporarily Restricted",
                account_type=AccountType.REVENUE.value,
                currency="USD",
            )
        )

        # 2. Setup Donor
        donor_res = create_donor(
            CreateDonorInput(
                context=self.admin_ctx,
                name="Bill & Melinda Gates Foundation",
                donor_type=DonorType.FOUNDATION.value,
                email="contact@gatesfoundation.org",
            )
        )
        self.donor_id = donor_res.donor_id

    def test_record_donation_automatically_posts_gl_entry(self) -> None:
        """When a donation is recorded, a balanced journal entry is automatically posted
        to the General Ledger: Dr 1010 Cash, Cr 3100 Restricted Revenue.
        """
        initial_je_count = len(list_journal_entries(self.admin_ctx))

        donation_res = record_donation(
            RecordDonationInput(
                context=self.admin_ctx,
                donor_id=self.donor_id,
                amount=Decimal("50000.00"),
                currency="USD",
                payment_method=PaymentMethod.BANK_TRANSFER.value,
                reference="WIRE-REF-89124",
                received_at=datetime(2026, 11, 23, 10, 0, tzinfo=UTC),
            )
        )

        # Verify posted JournalEntry was created
        all_jes = list_journal_entries(self.admin_ctx)
        assert len(all_jes) == initial_je_count + 1

        je = next((j for j in all_jes if "WIRE-REF-89124" in j.memo or str(donation_res.donation_id) in j.memo), None)
        assert je is not None
        assert je.status == JournalEntryStatus.POSTED.value
        assert je.currency == "USD"
        assert "Auto-GL: Donation received from Bill & Melinda Gates Foundation" in je.memo

        # Fetch lines and verify debits and credits
        je_detail = get_journal_entry(je.id, self.admin_ctx)
        assert je_detail.total_debits == Decimal("50000.00")
        assert je_detail.total_credits == Decimal("50000.00")

        lines_by_code = {line.account_code: line for line in je_detail.lines}
        assert "1010" in lines_by_code
        assert "3100" in lines_by_code

        assert lines_by_code["1010"].debit == Decimal("50000.00")
        assert lines_by_code["1010"].credit == Decimal("0.00")
        assert lines_by_code["3100"].debit == Decimal("0.00")
        assert lines_by_code["3100"].credit == Decimal("50000.00")

    def test_record_donation_linked_to_grant_sets_grant_id_on_gl_entry(self) -> None:
        """When a donation is linked to a grant, the resulting GL entry preserves
        the grant_id link for donor reporting and restricted funding traceability.
        """
        grant_res = create_grant(
            CreateGrantInput(
                context=self.admin_ctx,
                donor_id=self.donor_id,
                title="Emergency Water & Sanitation Initiative",
                reference_code="GRANT-WASH-2026",
                total_amount=Decimal("200000.00"),
                currency="USD",
                start_date=datetime(2026, 1, 1).date(),
                end_date=datetime(2026, 12, 31).date(),
            )
        )
        award_grant(AwardGrantInput(context=self.admin_ctx, grant_id=grant_res.grant_id))
        activate_grant(ActivateGrantInput(context=self.admin_ctx, grant_id=grant_res.grant_id))

        donation_res = record_donation(
            RecordDonationInput(
                context=self.admin_ctx,
                donor_id=self.donor_id,
                grant_id=grant_res.grant_id,
                amount=Decimal("25000.00"),
                currency="USD",
                payment_method=PaymentMethod.BANK_TRANSFER.value,
                reference="GRANT-TRANCHE-1",
            )
        )
        assert donation_res.donation_id is not None

        je = next((j for j in list_journal_entries(self.admin_ctx) if "GRANT-TRANCHE-1" in j.memo), None)
        assert je is not None
        assert "(Grant-linked)" in je.memo

        je_detail = get_journal_entry(je.id, self.admin_ctx)
        assert je_detail.grant_id == grant_res.grant_id
        assert je_detail.total_debits == Decimal("25000.00")
        assert je_detail.total_credits == Decimal("25000.00")

    def test_graceful_degradation_when_accounts_not_configured(self) -> None:
        """When an organization hasn't configured GL accounts (1010, 3100),
        donations are recorded cleanly without failing or partial state corruption.
        """
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid4(),
        )
        new_org = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Community Help Group",
                slug=f"chg-{uuid4().hex[:6]}",
            )
        )
        chg_ctx = ExecutionContext(
            organization_id=new_org.organization_id,
            actor_type=ActorType.USER,
            actor_id=uuid4(),
            actor_role=Role.ADMIN.value,
            correlation_id=uuid4(),
        )

        donor_res = create_donor(
            CreateDonorInput(
                context=chg_ctx,
                name="Local Supporter",
                donor_type=DonorType.INDIVIDUAL.value,
            )
        )

        don_res = record_donation(
            RecordDonationInput(
                context=chg_ctx,
                donor_id=donor_res.donor_id,
                amount=Decimal("150.00"),
            )
        )
        assert don_res.donation_id is not None
        # No journal entry created for new_org
        assert len(list_journal_entries(chg_ctx)) == 0
