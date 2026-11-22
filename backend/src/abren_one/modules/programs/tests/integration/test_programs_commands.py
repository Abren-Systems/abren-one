import uuid

import pytest
from django.contrib.auth import get_user_model

from abren_one.modules.organizations.public import (
    CreateOrganizationInput as CreateOrgInput,
)
from abren_one.modules.organizations.public import (
    create_organization,
)
from abren_one.modules.programs.application.commands.create_activity import (
    CreateActivityInput,
)
from abren_one.modules.programs.application.commands.create_activity import (
    execute as create_activity,
)
from abren_one.modules.programs.application.commands.create_program import (
    CreateProgramInput,
)
from abren_one.modules.programs.application.commands.create_program import (
    execute as create_program,
)
from abren_one.modules.programs.application.commands.create_project import (
    CreateProjectInput,
)
from abren_one.modules.programs.application.commands.create_project import (
    execute as create_project,
)
from abren_one.modules.programs.application.commands.update_activity import (
    UpdateActivityInput,
)
from abren_one.modules.programs.application.commands.update_activity import (
    execute as update_activity,
)
from abren_one.modules.programs.application.commands.update_program import (
    UpdateProgramInput,
)
from abren_one.modules.programs.application.commands.update_program import (
    execute as update_program,
)
from abren_one.modules.programs.application.commands.update_project import (
    UpdateProjectInput,
)
from abren_one.modules.programs.application.commands.update_project import (
    execute as update_project,
)
from abren_one.modules.programs.application.exceptions import (
    ActivityNotFoundError,
    InvalidActivityTransitionError,
    InvalidProgramTransitionError,
    InvalidProjectTransitionError,
    ProgramError,
    ProgramNotFoundError,
    ProjectNotFoundError,
)
from abren_one.modules.programs.application.queries.get_activity import (
    execute as get_activity,
)
from abren_one.modules.programs.application.queries.get_program import (
    execute as get_program,
)
from abren_one.modules.programs.application.queries.get_project import (
    execute as get_project,
)
from abren_one.modules.programs.application.queries.list_activities import (
    execute as list_activities,
)
from abren_one.modules.programs.application.queries.list_programs import (
    execute as list_programs,
)
from abren_one.modules.programs.application.queries.list_projects import (
    execute as list_projects,
)
from abren_one.modules.programs.domain.value_objects import (
    ActivityStatus,
    ProgramStatus,
    ProjectStatus,
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
            actor_role="admin",
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
            actor_role="admin",
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
            actor_role="admin",
        )
        prog = create_program(CreateProgramInput(context=ctx_a, name="Org A Program"))

        # Org B should not find Org A's program (fail-closed tenant isolation)
        with pytest.raises(ProgramNotFoundError):
            get_program(organization_id=org_b.organization_id, program_id=prog.program_id)

    def test_update_program_and_status_transitions(self) -> None:
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org = create_organization(CreateOrgInput(context=init_ctx, name="Prog Org", slug="prog-update-org"))
        ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org.organization_id,
            correlation_id=uuid.uuid4(),
            actor_role="admin",
        )

        prog = create_program(CreateProgramInput(context=ctx, name="Initial Name"))
        assert prog.program_id is not None

        # Valid update
        updated = update_program(
            UpdateProgramInput(
                context=ctx,
                program_id=prog.program_id,
                name="Updated Name",
                description="New desc",
                status=ProgramStatus.COMPLETED.value,
            )
        )
        assert updated.status == ProgramStatus.COMPLETED.value

        details = get_program(organization_id=org.organization_id, program_id=prog.program_id)
        assert details.name == "Updated Name"
        assert details.description == "New desc"
        assert details.status == ProgramStatus.COMPLETED.value

        # Invalid transition: COMPLETED -> ACTIVE
        with pytest.raises(InvalidProgramTransitionError):
            update_program(
                UpdateProgramInput(
                    context=ctx,
                    program_id=prog.program_id,
                    status=ProgramStatus.ACTIVE.value,
                )
            )

    def test_project_lifecycle_and_queries(self) -> None:
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org = create_organization(CreateOrgInput(context=init_ctx, name="Project Org", slug="proj-org"))
        ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org.organization_id,
            correlation_id=uuid.uuid4(),
            actor_role="admin",
        )

        prog = create_program(CreateProgramInput(context=ctx, name="Main Program"))

        # Create project
        proj = create_project(
            CreateProjectInput(
                context=ctx,
                program_id=prog.program_id,
                name="Phase 1 Clinic Build",
                description="Construction",
                budget_currency="USD",
            )
        )
        assert proj.project_id is not None

        # Duplicate project name in same program fails
        with pytest.raises(ProgramError, match="already exists"):
            create_project(
                CreateProjectInput(
                    context=ctx,
                    program_id=prog.program_id,
                    name="Phase 1 Clinic Build",
                )
            )

        # Get and list projects
        details = get_project(organization_id=org.organization_id, project_id=proj.project_id)
        assert details.name == "Phase 1 Clinic Build"
        assert details.status == ProjectStatus.PLANNING.value

        projects = list_projects(organization_id=org.organization_id, program_id=prog.program_id)
        assert len(projects) == 1
        assert projects[0].id == proj.project_id

        # Update project status
        upd = update_project(
            UpdateProjectInput(
                context=ctx,
                project_id=proj.project_id,
                status=ProjectStatus.IN_PROGRESS.value,
            )
        )
        assert upd.status == ProjectStatus.IN_PROGRESS.value

        # Invalid transition: IN_PROGRESS -> PLANNING
        with pytest.raises(InvalidProjectTransitionError):
            update_project(
                UpdateProjectInput(
                    context=ctx,
                    project_id=proj.project_id,
                    status=ProjectStatus.PLANNING.value,
                )
            )

        # Not found query
        with pytest.raises(ProjectNotFoundError):
            get_project(organization_id=org.organization_id, project_id=uuid.uuid4())

    def test_activity_lifecycle_and_queries(self) -> None:
        init_ctx = ExecutionContext(
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            organization_id=None,
            correlation_id=uuid.uuid4(),
        )
        org = create_organization(CreateOrgInput(context=init_ctx, name="Activity Org", slug="act-org"))
        ctx = ExecutionContext(
            actor_type=ActorType.USER,
            actor_id=uuid.uuid4(),
            organization_id=org.organization_id,
            correlation_id=uuid.uuid4(),
            actor_role="admin",
        )

        prog = create_program(CreateProgramInput(context=ctx, name="Act Program"))
        proj = create_project(CreateProjectInput(context=ctx, program_id=prog.program_id, name="Act Project"))

        # Create activity
        act = create_activity(
            CreateActivityInput(
                context=ctx,
                project_id=proj.project_id,
                name="Lay Foundations",
            )
        )
        assert act.activity_id is not None

        # Get and list activities
        act_details = get_activity(organization_id=org.organization_id, activity_id=act.activity_id)
        assert act_details.name == "Lay Foundations"
        assert act_details.status == ActivityStatus.PENDING.value

        activities = list_activities(organization_id=org.organization_id, project_id=proj.project_id)
        assert len(activities) == 1
        assert activities[0].id == act.activity_id

        # Update activity status
        upd = update_activity(
            UpdateActivityInput(
                context=ctx,
                activity_id=act.activity_id,
                status=ActivityStatus.IN_PROGRESS.value,
            )
        )
        assert upd.status == ActivityStatus.IN_PROGRESS.value

        # Invalid transition: IN_PROGRESS -> PENDING
        with pytest.raises(InvalidActivityTransitionError):
            update_activity(
                UpdateActivityInput(
                    context=ctx,
                    activity_id=act.activity_id,
                    status=ActivityStatus.PENDING.value,
                )
            )

        # Not found query
        with pytest.raises(ActivityNotFoundError):
            get_activity(organization_id=org.organization_id, activity_id=uuid.uuid4())
