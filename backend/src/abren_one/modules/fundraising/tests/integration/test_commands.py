import uuid
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

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
from abren_one.modules.fundraising.application.exceptions import (
    FundraisingError,
    GrantMismatchError,
    InactiveDonorError,
    InvalidDonationAmountError,
)
from abren_one.modules.fundraising.application.queries.get_donor import (
    execute as get_donor,
)
from abren_one.modules.fundraising.application.queries.get_grant import (
    execute as get_grant,
)
from abren_one.modules.fundraising.application.queries.list_donations import (
    execute as list_donations,
)
from abren_one.modules.fundraising.application.queries.list_donors import (
    execute as list_donors,
)
from abren_one.modules.fundraising.application.queries.list_grants import (
    execute as list_grants,
)
from abren_one.modules.fundraising.domain.value_objects import (
    DonorStatus,
    GrantStatus,
)
from abren_one.modules.fundraising.models import Donor, Grant
from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.modules.programs.public import (
    CreateProgramInput,
    create_program,
)
from abren_one.platform.audit.models import AuditEvent
from abren_one.platform.common.context import ActorType, ExecutionContext

User = get_user_model()


@pytest.mark.django_db
class TestFundraisingCommandsAndQueries:
    def setup_method(self) -> None:
        self.user = User.objects.create_user(username="fundraiser", password="password")
        self.correlation_id = uuid.uuid4()
        init_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=self.user.id,
            organization_id=None,
            correlation_id=self.correlation_id,
        )
        org_result = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Global Aid",
                slug=f"global-aid-{uuid.uuid4().hex[:6]}",
            )
        )
        self.org_id = org_result.organization_id
        self.context = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=self.user.id,
            organization_id=self.org_id,
            correlation_id=self.correlation_id,
            actor_role="admin",
        )

    def test_create_donor_and_audit(self) -> None:
        result = create_donor(
            CreateDonorInput(
                context=self.context,
                name="Acme Foundation",
                donor_type="foundation",
                email="contact@acme.org",
            )
        )
        assert result.donor_id is not None

        donor = get_donor(donor_id=result.donor_id, organization_id=self.org_id)
        assert donor.name == "Acme Foundation"
        assert donor.donor_type == "foundation"
        assert donor.email == "contact@acme.org"
        assert donor.is_active is True

        donors = list_donors(organization_id=self.org_id)
        assert len(donors) == 1
        assert donors[0].id == result.donor_id

        # Verify audit event
        audit = AuditEvent.objects.filter(target_id=result.donor_id, action="fundraising.donor.created").first()
        assert audit is not None
        assert audit.organization_id == self.org_id

    def test_duplicate_donor_name_fails(self) -> None:
        create_donor(CreateDonorInput(context=self.context, name="Alice Walker"))
        with pytest.raises(FundraisingError, match="already exists"):
            create_donor(CreateDonorInput(context=self.context, name="Alice Walker"))

    def test_create_grant_with_program_link(self) -> None:
        # Create program via programs module public API
        prog_result = create_program(
            CreateProgramInput(
                context=self.context,
                name="Emergency Response",
            )
        )
        donor_res = create_donor(CreateDonorInput(context=self.context, name="UN Foundation"))

        grant_res = create_grant(
            CreateGrantInput(
                context=self.context,
                donor_id=donor_res.donor_id,
                title="Disaster Relief Grant",
                reference_code="UN-DR-2026",
                total_amount=Decimal("250000.00"),
                start_date=date(2026, 1, 1),
                end_date=date(2026, 12, 31),
                program_id=prog_result.program_id,
            )
        )

        grant = get_grant(grant_id=grant_res.grant_id, organization_id=self.org_id)
        assert grant.title == "Disaster Relief Grant"
        assert grant.total_amount == Decimal("250000.00")
        assert grant.program_id == prog_result.program_id
        assert grant.status == GrantStatus.PROPOSED.value

        grants = list_grants(organization_id=self.org_id)
        assert len(grants) == 1
        assert grants[0].id == grant_res.grant_id

    def test_create_grant_invalid_dates_fails(self) -> None:
        donor_res = create_donor(CreateDonorInput(context=self.context, name="Test Donor"))
        with pytest.raises(FundraisingError, match="end_date cannot precede start_date"):
            create_grant(
                CreateGrantInput(
                    context=self.context,
                    donor_id=donor_res.donor_id,
                    title="Invalid Dates Grant",
                    reference_code="INV-DATE-1",
                    total_amount=Decimal("1000.00"),
                    start_date=date(2026, 12, 31),
                    end_date=date(2026, 1, 1),
                )
            )

    def test_create_grant_inactive_donor_fails(self) -> None:
        donor_res = create_donor(CreateDonorInput(context=self.context, name="Inactive Donor"))
        Donor.objects.filter(id=donor_res.donor_id).update(status=DonorStatus.INACTIVE.value)

        with pytest.raises(InactiveDonorError):
            create_grant(
                CreateGrantInput(
                    context=self.context,
                    donor_id=donor_res.donor_id,
                    title="Grant to Inactive",
                    reference_code="INACT-1",
                    total_amount=Decimal("5000.00"),
                    start_date=date(2026, 1, 1),
                    end_date=date(2026, 12, 31),
                )
            )

    def test_record_donation_standalone(self) -> None:
        donor_res = create_donor(CreateDonorInput(context=self.context, name="Generous Benefactor"))
        donation_res = record_donation(
            RecordDonationInput(
                context=self.context,
                donor_id=donor_res.donor_id,
                amount=Decimal("10000.00"),
                currency="USD",
                payment_method="check",
                reference="CHK-9876",
            )
        )
        assert donation_res.donation_id is not None

        donations = list_donations(organization_id=self.org_id)
        assert len(donations) == 1
        assert donations[0].amount == Decimal("10000.00")
        assert donations[0].donor_name == "Generous Benefactor"
        assert donations[0].grant_id is None

        # Verify audit
        audit = AuditEvent.objects.filter(
            target_id=donation_res.donation_id,
            action="fundraising.donation.recorded",
        ).first()
        assert audit is not None
        assert audit.organization_id == self.org_id

    def test_record_donation_linked_to_grant(self) -> None:
        donor_res = create_donor(CreateDonorInput(context=self.context, name="Global Trust"))
        grant_res = create_grant(
            CreateGrantInput(
                context=self.context,
                donor_id=donor_res.donor_id,
                title="WASH Grant",
                reference_code="WASH-2026",
                total_amount=Decimal("50000.00"),
                start_date=date(2026, 1, 1),
                end_date=date(2026, 12, 31),
            )
        )
        # Transition grant to active
        Grant.objects.filter(id=grant_res.grant_id).update(status=GrantStatus.ACTIVE.value)

        record_donation(
            RecordDonationInput(
                context=self.context,
                donor_id=donor_res.donor_id,
                grant_id=grant_res.grant_id,
                amount=Decimal("25000.00"),
            )
        )

        donations = list_donations(organization_id=self.org_id)
        assert len(donations) == 1
        assert donations[0].grant_id == grant_res.grant_id
        assert donations[0].amount == Decimal("25000.00")

    def test_record_donation_grant_mismatch_fails(self) -> None:
        donor_a = create_donor(CreateDonorInput(context=self.context, name="Donor A"))
        donor_b = create_donor(CreateDonorInput(context=self.context, name="Donor B"))
        grant = create_grant(
            CreateGrantInput(
                context=self.context,
                donor_id=donor_a.donor_id,
                title="Grant A",
                reference_code="GA-1",
                total_amount=Decimal("1000.00"),
                start_date=date(2026, 1, 1),
                end_date=date(2026, 12, 31),
            )
        )
        Grant.objects.filter(id=grant.grant_id).update(status=GrantStatus.ACTIVE.value)

        # Try to record donation from Donor B against Donor A's grant
        with pytest.raises(GrantMismatchError):
            record_donation(
                RecordDonationInput(
                    context=self.context,
                    donor_id=donor_b.donor_id,
                    grant_id=grant.grant_id,
                    amount=Decimal("500.00"),
                )
            )

    def test_record_donation_zero_amount_fails(self) -> None:
        donor = create_donor(CreateDonorInput(context=self.context, name="Donor Zero"))
        with pytest.raises(InvalidDonationAmountError):
            record_donation(
                RecordDonationInput(
                    context=self.context,
                    donor_id=donor.donor_id,
                    amount=Decimal("0.00"),
                )
            )
