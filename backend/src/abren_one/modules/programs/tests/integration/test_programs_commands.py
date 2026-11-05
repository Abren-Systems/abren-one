import uuid

import pytest
from django.contrib.auth import get_user_model

from abren_one.modules.organizations.public import (
    CreateOrganizationInput as CreateOrgInput,
)
from abren_one.modules.organizations.public import (
    create_organization,
)
from abren_one.modules.programs.application.commands.create_program import (
    CreateProgramInput,
)
from abren_one.modules.programs.application.commands.create_program import (
    execute as create_program,
)
from abren_one.modules.programs.application.exceptions import (
    ProgramError,
    ProgramNotFoundError,
)
from abren_one.modules.programs.application.queries.get_program import (
    execute as get_program,
)
from abren_one.modules.programs.application.queries.list_programs import (
    execute as list_programs,
)
from abren_one.platform.audit.models import AuditEvent
from abren_one.platform.common.context import ActorType, ExecutionContext

User = get_user_model()


@pytest.mark.django_db
class TestProgramsCommandsAndQueries:
    def test_create_program_and_audit(self) -> None:
        user = User.objects.create_user(username="program_mgr", password="password")
        correlation_id = uuid.uuid4()
        init_ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=user.id,
            organization_id=None,
            correlation_id=correlation_id,
        )
        org_result = create_organization(CreateOrgInput(context=init_ctx, name="Health NGO", slug="health-ngo"))

        context = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=user.id,
            organization_id=org_result.organization_id,
            correlation_id=correlation_id,
        )

        result = create_program(
            CreateProgramInput(
                context=context,
                name="Maternal Health Initiative",
                description="Supporting maternal healthcare across clinics.",
            )
        )

        details = get_program(organization_id=org_result.organization_id, program_id=result.program_id)
        assert details.name == "Maternal Health Initiative"
        assert details.is_active is True

        programs = list_programs(organization_id=org_result.organization_id)
        assert len(programs) == 1
        assert programs[0].id == result.program_id

        # Verify audit trail
        audit = AuditEvent.objects.filter(target_id=result.program_id).first()
        assert audit is not None
        assert audit.action == "program.created"
        assert audit.organization_id == org_result.organization_id

    def test_duplicate_program_name_in_same_org_fails(self) -> None:
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org_result = create_organization(CreateOrgInput(context=init_ctx, name="Edu NGO", slug="edu-ngo"))
        context = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org_result.organization_id,
            correlation_id=uuid.uuid4(),
        )

        create_program(CreateProgramInput(context=context, name="Literacy 2026"))
        with pytest.raises(ProgramError, match="already exists"):
            create_program(CreateProgramInput(context=context, name="Literacy 2026"))

    def test_program_in_different_org_not_found(self) -> None:
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org_a = create_organization(CreateOrgInput(context=init_ctx, name="Org A", slug="prog-org-a"))
        org_b = create_organization(CreateOrgInput(context=init_ctx, name="Org B", slug="prog-org-b"))

        ctx_a = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org_a.organization_id,
            correlation_id=uuid.uuid4(),
        )
        prog = create_program(CreateProgramInput(context=ctx_a, name="Org A Program"))

        # Org B should not find Org A's program (fail-closed tenant isolation)
        with pytest.raises(ProgramNotFoundError):
            get_program(organization_id=org_b.organization_id, program_id=prog.program_id)
