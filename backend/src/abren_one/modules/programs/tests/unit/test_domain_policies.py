from abren_one.modules.programs.domain.policies import (
    can_transition_activity_status,
    can_transition_program_status,
    can_transition_project_status,
)
from abren_one.modules.programs.domain.value_objects import (
    ActivityStatus,
    ProgramStatus,
    ProjectStatus,
)


class TestProgramPolicies:
    def test_program_same_status_allowed(self) -> None:
        assert can_transition_program_status(ProgramStatus.ACTIVE, ProgramStatus.ACTIVE) is True

    def test_program_valid_transitions(self) -> None:
        assert can_transition_program_status(ProgramStatus.PLANNING, ProgramStatus.ACTIVE) is True
        assert can_transition_program_status(ProgramStatus.ACTIVE, ProgramStatus.COMPLETED) is True
        assert can_transition_program_status(ProgramStatus.COMPLETED, ProgramStatus.ARCHIVED) is True

    def test_program_invalid_transitions(self) -> None:
        assert can_transition_program_status(ProgramStatus.COMPLETED, ProgramStatus.ACTIVE) is False
        assert can_transition_program_status(ProgramStatus.ARCHIVED, ProgramStatus.ACTIVE) is False

    def test_project_valid_transitions(self) -> None:
        assert can_transition_project_status(ProjectStatus.PLANNING, ProjectStatus.IN_PROGRESS) is True
        assert can_transition_project_status(ProjectStatus.IN_PROGRESS, ProjectStatus.COMPLETED) is True
        assert can_transition_project_status(ProjectStatus.IN_PROGRESS, ProjectStatus.ON_HOLD) is True
        assert can_transition_project_status(ProjectStatus.ON_HOLD, ProjectStatus.IN_PROGRESS) is True

    def test_project_invalid_transitions(self) -> None:
        assert can_transition_project_status(ProjectStatus.COMPLETED, ProjectStatus.PLANNING) is False
        assert can_transition_project_status(ProjectStatus.COMPLETED, ProjectStatus.IN_PROGRESS) is False

    def test_activity_valid_transitions(self) -> None:
        assert can_transition_activity_status(ActivityStatus.PENDING, ActivityStatus.IN_PROGRESS) is True
        assert can_transition_activity_status(ActivityStatus.IN_PROGRESS, ActivityStatus.COMPLETED) is True
        assert can_transition_activity_status(ActivityStatus.IN_PROGRESS, ActivityStatus.BLOCKED) is True
        assert can_transition_activity_status(ActivityStatus.BLOCKED, ActivityStatus.IN_PROGRESS) is True

    def test_activity_invalid_transitions(self) -> None:
        assert can_transition_activity_status(ActivityStatus.COMPLETED, ActivityStatus.PENDING) is False
        assert can_transition_activity_status(ActivityStatus.COMPLETED, ActivityStatus.IN_PROGRESS) is False
