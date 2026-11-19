"""End-to-End NGO Lifecycle Integration Test.

Exercises the complete operational workflow across all four business domains
and platform services through public APIs only (§3.1, §3.5):

1. Provision Organization, Branch, and Department (organizations)
2. Create strategic Program, Project, and operational Activity (programs)
3. Register institutional Donor, award Grant, and record Donation (fundraising)
4. Register Beneficiary and record Service Delivery tied to Program/Activity (beneficiaries)
5. Verify end-to-end data integrity, tenant isolation, and audit trail.
"""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from abren_one.modules.beneficiaries.public import (
    RecordServiceDeliveryInput,
    RegisterBeneficiaryInput,
    get_beneficiary,
    get_service_delivery,
    list_service_deliveries,
    record_service_delivery,
    register_beneficiary,
)
from abren_one.modules.fundraising.public import (
    CreateDonorInput,
    CreateGrantInput,
    RecordDonationInput,
    create_donor,
    create_grant,
    get_donor,
    get_grant,
    list_donations,
    record_donation,
)
from abren_one.modules.organizations.public import (
    CreateBranchInput,
    CreateDepartmentInput,
    CreateOrganizationInput,
    create_branch,
    create_department,
    create_organization,
    get_organization,
)
from abren_one.modules.programs.public import (
    CreateActivityInput,
    CreateProgramInput,
    CreateProjectInput,
    create_activity,
    create_program,
    create_project,
    get_activity,
    get_program,
    get_project,
)
from abren_one.platform.audit.models import AuditEvent
from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.mark.django_db
class TestNgoLifecycleWorkflow:
    """Verifies that an NGO can run its full operating lifecycle through public interfaces."""

    def test_full_ngo_lifecycle_and_audit_trail(self) -> None:
        user = get_user_model().objects.create_user(
            username=f"director_{uuid.uuid4().hex[:8]}",
            password="testpassword123",
        )
        actor_id = user.id
        correlation_id = uuid.uuid4()

        # -------------------------------------------------------------------
        # 1. Provision Organization, Branch, and Department
        # -------------------------------------------------------------------
        init_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=actor_id,
            organization_id=None,
            correlation_id=correlation_id,
        )
        org_res = create_organization(
            CreateOrganizationInput(
                context=init_ctx,
                name="Horn of Africa Relief",
                slug="horn-of-africa-relief",
            )
        )
        org_id = org_res.organization_id

        # Context scoped to the new tenant
        tenant_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=actor_id,
            organization_id=org_id,
            correlation_id=correlation_id,
        )

        branch_res = create_branch(
            CreateBranchInput(
                context=tenant_ctx,
                name="Somali Region Field Office",
                code="SRFO",
            )
        )
        assert branch_res.branch_id is not None

        dept_res = create_department(
            CreateDepartmentInput(
                context=tenant_ctx,
                name="Food Security & Livelihoods",
                code="FSL",
            )
        )
        assert dept_res.department_id is not None

        org = get_organization(organization_id=org_id)
        assert org.name == "Horn of Africa Relief"
        assert org.is_active is True

        # -------------------------------------------------------------------
        # 2. Setup Programs, Projects, and Activities
        # -------------------------------------------------------------------
        prog_res = create_program(
            CreateProgramInput(
                context=tenant_ctx,
                name="Drought Resilience & Nutrition Initiative",
                description="Long-term drought mitigation and child nutrition support.",
            )
        )
        program_id = prog_res.program_id

        proj_res = create_project(
            CreateProjectInput(
                context=tenant_ctx,
                program_id=program_id,
                name="Emergency Water & Food Trucking",
                description="Targeted water and therapeutic food distribution.",
            )
        )
        project_id = proj_res.project_id

        act_res = create_activity(
            CreateActivityInput(
                context=tenant_ctx,
                project_id=project_id,
                name="Bi-weekly High-Energy Biscuit Distribution",
                due_date=date(2026, 12, 31),
            )
        )
        activity_id = act_res.activity_id

        program = get_program(program_id=program_id, organization_id=org_id)
        assert program.name == "Drought Resilience & Nutrition Initiative"
        project = get_project(project_id=project_id, organization_id=org_id)
        assert project.program_id == program_id
        activity = get_activity(activity_id=activity_id, organization_id=org_id)
        assert activity.project_id == project_id

        # -------------------------------------------------------------------
        # 3. Fundraising: Register Donor, Award Grant, Record Donation
        # -------------------------------------------------------------------
        donor_res = create_donor(
            CreateDonorInput(
                context=tenant_ctx,
                name="International Humanitarian Foundation",
                donor_type="foundation",
                email="grants@ihf.org",
                phone="+442079460991",
            )
        )
        donor_id = donor_res.donor_id

        grant_res = create_grant(
            CreateGrantInput(
                context=tenant_ctx,
                donor_id=donor_id,
                title="Horn Drought Relief Emergency Grant",
                reference_code="IHF-ET-2026-09",
                total_amount=Decimal("250000.00"),
                start_date=date(2026, 1, 1),
                end_date=date(2026, 12, 31),
                currency="USD",
                program_id=program_id,
            )
        )
        grant_id = grant_res.grant_id

        # Transition grant to active status so donations can be recorded against it
        from abren_one.modules.fundraising.domain.value_objects import GrantStatus
        from abren_one.modules.fundraising.models import Grant

        Grant.objects.filter(id=grant_id).update(status=GrantStatus.ACTIVE.value)

        donation_res = record_donation(
            RecordDonationInput(
                context=tenant_ctx,
                donor_id=donor_id,
                grant_id=grant_id,
                program_id=program_id,
                amount=Decimal("75000.00"),
                currency="USD",
                payment_method="bank_transfer",
                reference="WIRE-IHF-2026-TRANCHE1",
            )
        )
        donation_id = donation_res.donation_id

        donor = get_donor(donor_id=donor_id, organization_id=org_id)
        assert donor.name == "International Humanitarian Foundation"
        grant = get_grant(grant_id=grant_id, organization_id=org_id)
        assert grant.total_amount == Decimal("250000.00")
        assert grant.program_id == program_id
        donations = list_donations(organization_id=org_id)
        assert len(donations) == 1
        assert donations[0].id == donation_id
        assert donations[0].amount == Decimal("75000.00")

        # -------------------------------------------------------------------
        # 4. Beneficiaries: Register Beneficiary & Deliver Service
        # -------------------------------------------------------------------
        ben_res = register_beneficiary(
            RegisterBeneficiaryInput(
                context=tenant_ctx,
                beneficiary_type="household",
                household_name="Abdi Warsame Household",
                identification_number="BEN-ETH-2026-0042",
                vulnerability_level="critical",
                contact_phone="+251911223344",
                contact_address="Gode Camp Zone 3, Shebelle",
                notes="Family of 6, severe drought impact.",
            )
        )
        beneficiary_id = ben_res.beneficiary_id

        delivery_res = record_service_delivery(
            RecordServiceDeliveryInput(
                context=tenant_ctx,
                beneficiary_id=beneficiary_id,
                service_type="food_assistance",
                delivery_date=date(2026, 11, 15),
                quantity=Decimal("50.00"),
                unit="kg",
                program_id=program_id,
                activity_id=activity_id,
                notes="Delivered 50kg supplementary therapeutic feeding packs.",
            )
        )
        delivery_id = delivery_res.delivery_id

        beneficiary = get_beneficiary(beneficiary_id=beneficiary_id, organization_id=org_id)
        assert beneficiary.household_name == "Abdi Warsame Household"
        assert beneficiary.is_active is True
        assert beneficiary.vulnerability_level == "critical"

        delivery = get_service_delivery(delivery_id=delivery_id, organization_id=org_id)
        assert delivery.quantity == Decimal("50.00")
        assert delivery.unit == "kg"
        assert delivery.program_id == program_id
        assert delivery.activity_id == activity_id
        assert delivery.status == "delivered"

        deliveries = list_service_deliveries(organization_id=org_id, beneficiary_id=beneficiary_id)
        assert len(deliveries) == 1
        assert deliveries[0].id == delivery_id

        # -------------------------------------------------------------------
        # 5. Audit Trail Verification
        # -------------------------------------------------------------------
        audit_events = list(AuditEvent.objects.filter(organization_id=org_id).order_by("timestamp"))
        actions = [e.action for e in audit_events]

        assert "branch.created" in actions
        assert "department.created" in actions
        assert "program.created" in actions
        assert "project.created" in actions
        assert "activity.created" in actions
        assert "fundraising.donor.created" in actions
        assert "fundraising.grant.created" in actions
        assert "fundraising.donation.recorded" in actions
        assert "beneficiary.registered" in actions
        assert "service_delivery.recorded" in actions

        for event in audit_events:
            assert event.outcome == "success"
            assert event.correlation_id == correlation_id
            assert event.actor_id == actor_id

    def test_cross_tenant_isolation_in_service_delivery(self) -> None:
        """Cross-tenant boundaries must block access and cross-module referencing."""
        user = get_user_model().objects.create_user(
            username=f"officer_{uuid.uuid4().hex[:8]}",
            password="testpassword123",
        )
        actor_id = user.id
        corr_id = uuid.uuid4()
        init_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=actor_id,
            organization_id=None,
            correlation_id=corr_id,
        )

        org_a = create_organization(
            CreateOrganizationInput(context=init_ctx, name="Org Alpha", slug="org-alpha")
        ).organization_id
        org_b = create_organization(
            CreateOrganizationInput(context=init_ctx, name="Org Beta", slug="org-beta")
        ).organization_id

        ctx_a = ExecutionContext(
            actor_type=ActorType.USER, actor_id=actor_id, organization_id=org_a, correlation_id=corr_id
        )
        ctx_b = ExecutionContext(
            actor_type=ActorType.USER, actor_id=actor_id, organization_id=org_b, correlation_id=corr_id
        )

        # Beneficiary registered in Org A
        ben_a = register_beneficiary(
            RegisterBeneficiaryInput(
                context=ctx_a,
                first_name="Fatima",
                last_name="Ali",
                identification_number="ALPHA-001",
            )
        ).beneficiary_id

        # Program registered in Org B
        prog_b = create_program(CreateProgramInput(context=ctx_b, name="Org B Health Program")).program_id

        # Delivery in Org A attempting to link to Org B's program must fail
        from abren_one.modules.beneficiaries.public import BeneficiaryError

        with pytest.raises(BeneficiaryError, match="Program .* not found"):
            record_service_delivery(
                RecordServiceDeliveryInput(
                    context=ctx_a,
                    beneficiary_id=ben_a,
                    service_type="medical_support",
                    delivery_date=date.today(),
                    program_id=prog_b,
                )
            )
