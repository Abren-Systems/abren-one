import uuid
from decimal import Decimal

import pytest

from abren_one.modules.beneficiaries.application.commands.record_service_delivery import (
    RecordServiceDeliveryInput,
)
from abren_one.modules.beneficiaries.application.commands.record_service_delivery import (
    execute as record_service_delivery,
)
from abren_one.modules.beneficiaries.application.commands.register_beneficiary import (
    RegisterBeneficiaryInput,
)
from abren_one.modules.beneficiaries.application.commands.register_beneficiary import (
    execute as register_beneficiary,
)
from abren_one.modules.beneficiaries.application.commands.update_beneficiary import (
    UpdateBeneficiaryInput,
)
from abren_one.modules.beneficiaries.application.commands.update_beneficiary import (
    execute as update_beneficiary,
)
from abren_one.modules.beneficiaries.application.exceptions import (
    BeneficiaryError,
    BeneficiaryNotFoundError,
    InactiveBeneficiaryError,
    InvalidBeneficiaryTransitionError,
    ServiceDeliveryNotFoundError,
)
from abren_one.modules.beneficiaries.application.queries.get_beneficiary import (
    execute as get_beneficiary,
)
from abren_one.modules.beneficiaries.application.queries.get_service_delivery import (
    execute as get_service_delivery,
)
from abren_one.modules.beneficiaries.application.queries.list_beneficiaries import (
    execute as list_beneficiaries,
)
from abren_one.modules.beneficiaries.application.queries.list_service_deliveries import (
    execute as list_service_deliveries,
)
from abren_one.modules.beneficiaries.domain.value_objects import (
    BeneficiaryStatus,
    BeneficiaryType,
    ServiceType,
)
from abren_one.modules.organizations.public import (
    CreateOrganizationInput,
    create_organization,
)
from abren_one.modules.programs.public import (
    CreateActivityInput,
    CreateProgramInput,
    CreateProjectInput,
    create_activity,
    create_program,
    create_project,
)
from abren_one.platform.audit.models import AuditEvent
from abren_one.platform.common.context import ActorType, ExecutionContext


@pytest.mark.django_db
class TestBeneficiaryCommandsAndQueries:
    def test_register_and_query_beneficiary(self) -> None:
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org = create_organization(CreateOrganizationInput(context=init_ctx, name="Aide Org", slug="aide-org"))
        ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org.organization_id,
            correlation_id=uuid.uuid4(),
        )

        res = register_beneficiary(
            RegisterBeneficiaryInput(
                context=ctx,
                beneficiary_type=BeneficiaryType.INDIVIDUAL.value,
                identification_number="NAT-12345",
                first_name="Amina",
                last_name="Diallo",
                gender="female",
                contact_phone="+251911000000",
            )
        )
        assert res.beneficiary_id is not None

        details = get_beneficiary(
            organization_id=org.organization_id,
            beneficiary_id=res.beneficiary_id,
        )
        assert details.first_name == "Amina"
        assert details.last_name == "Diallo"
        assert details.display_name == "Amina Diallo"
        assert details.identification_number == "NAT-12345"
        assert details.is_active is True

        # Duplicate ID number in same org fails
        with pytest.raises(BeneficiaryError, match="already exists"):
            register_beneficiary(
                RegisterBeneficiaryInput(
                    context=ctx,
                    identification_number="NAT-12345",
                    first_name="Duplicate",
                )
            )

        # Audit event recorded
        audit = AuditEvent.objects.filter(
            action="beneficiary.registered",
            target_id=res.beneficiary_id,
        ).first()
        assert audit is not None
        assert audit.organization_id == org.organization_id

        # List query
        b_list = list_beneficiaries(organization_id=org.organization_id)
        assert len(b_list) == 1
        assert b_list[0].id == res.beneficiary_id

    def test_update_beneficiary_lifecycle(self) -> None:
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org = create_organization(CreateOrganizationInput(context=init_ctx, name="Aid Org 2", slug="aid-org-2"))
        ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org.organization_id,
            correlation_id=uuid.uuid4(),
        )

        res = register_beneficiary(
            RegisterBeneficiaryInput(
                context=ctx,
                beneficiary_type=BeneficiaryType.HOUSEHOLD.value,
                household_name="Diallo Family",
            )
        )

        # Update details
        upd = update_beneficiary(
            UpdateBeneficiaryInput(
                context=ctx,
                beneficiary_id=res.beneficiary_id,
                household_name="The Diallo Household",
                status=BeneficiaryStatus.GRADUATED.value,
            )
        )
        assert upd.status == BeneficiaryStatus.GRADUATED.value

        details = get_beneficiary(
            organization_id=org.organization_id,
            beneficiary_id=res.beneficiary_id,
        )
        assert details.household_name == "The Diallo Household"
        assert details.display_name == "The Diallo Household"
        assert details.status == BeneficiaryStatus.GRADUATED.value

        # Archive beneficiary
        update_beneficiary(
            UpdateBeneficiaryInput(
                context=ctx,
                beneficiary_id=res.beneficiary_id,
                status=BeneficiaryStatus.ARCHIVED.value,
            )
        )

        # Transition from terminal ARCHIVED to ACTIVE fails
        with pytest.raises(InvalidBeneficiaryTransitionError):
            update_beneficiary(
                UpdateBeneficiaryInput(
                    context=ctx,
                    beneficiary_id=res.beneficiary_id,
                    status=BeneficiaryStatus.ACTIVE.value,
                )
            )

    def test_record_service_delivery_with_program_and_activity(self) -> None:
        from datetime import date

        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org = create_organization(CreateOrganizationInput(context=init_ctx, name="Aid Org 3", slug="aid-org-3"))
        ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org.organization_id,
            correlation_id=uuid.uuid4(),
        )

        prog = create_program(CreateProgramInput(context=ctx, name="Emergency Nutrition"))
        proj = create_project(
            CreateProjectInput(
                context=ctx,
                program_id=prog.program_id,
                name="Food Kit Distribution",
            )
        )
        act = create_activity(
            CreateActivityInput(
                context=ctx,
                project_id=proj.project_id,
                name="Distribution Day 1",
            )
        )

        ben = register_beneficiary(
            RegisterBeneficiaryInput(
                context=ctx,
                first_name="Fatima",
                last_name="Ali",
            )
        )

        # Record delivery
        deliv = record_service_delivery(
            RecordServiceDeliveryInput(
                context=ctx,
                beneficiary_id=ben.beneficiary_id,
                service_type=ServiceType.FOOD_ASSISTANCE.value,
                delivery_date=date(2026, 3, 1),
                quantity=Decimal("50.00"),
                unit="kg",
                program_id=prog.program_id,
                activity_id=act.activity_id,
                notes="Standard food ration",
            )
        )
        assert deliv.delivery_id is not None

        # Query detail
        deliv_details = get_service_delivery(
            organization_id=org.organization_id,
            delivery_id=deliv.delivery_id,
        )
        assert deliv_details.service_type == ServiceType.FOOD_ASSISTANCE.value
        assert deliv_details.quantity == Decimal("50.00")
        assert deliv_details.unit == "kg"
        assert deliv_details.beneficiary_name == "Fatima Ali"
        assert deliv_details.program_id == prog.program_id
        assert deliv_details.activity_id == act.activity_id

        # Query list
        deliveries = list_service_deliveries(
            organization_id=org.organization_id,
            beneficiary_id=ben.beneficiary_id,
        )
        assert len(deliveries) == 1
        assert deliveries[0].id == deliv.delivery_id

        # Negative delivery quantity fails
        with pytest.raises(BeneficiaryError, match="non-negative"):
            record_service_delivery(
                RecordServiceDeliveryInput(
                    context=ctx,
                    beneficiary_id=ben.beneficiary_id,
                    service_type=ServiceType.FOOD_ASSISTANCE.value,
                    delivery_date=date(2026, 3, 1),
                    quantity=Decimal("-5.00"),
                )
            )

        # Service delivery to inactive/suspended beneficiary fails
        update_beneficiary(
            UpdateBeneficiaryInput(
                context=ctx,
                beneficiary_id=ben.beneficiary_id,
                status=BeneficiaryStatus.SUSPENDED.value,
            )
        )
        with pytest.raises(InactiveBeneficiaryError):
            record_service_delivery(
                RecordServiceDeliveryInput(
                    context=ctx,
                    beneficiary_id=ben.beneficiary_id,
                    service_type=ServiceType.FOOD_ASSISTANCE.value,
                    delivery_date=date(2026, 3, 1),
                )
            )

    def test_not_found_errors_on_invalid_id(self) -> None:
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org = create_organization(CreateOrganizationInput(context=init_ctx, name="Aid Org 4", slug="aid-org-4"))

        with pytest.raises(BeneficiaryNotFoundError):
            get_beneficiary(organization_id=org.organization_id, beneficiary_id=uuid.uuid4())

        with pytest.raises(ServiceDeliveryNotFoundError):
            get_service_delivery(organization_id=org.organization_id, delivery_id=uuid.uuid4())
