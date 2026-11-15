"""Domain policies for the Programs module.

Pure Python business rules governing program, project, and activity lifecycles.
Independent of ORM, database, and transport layers (§2.2).
"""

from __future__ import annotations

from abren_one.modules.programs.domain.value_objects import (
    ActivityStatus,
    ProgramStatus,
    ProjectStatus,
)

# Valid status transitions for programs
_VALID_PROGRAM_TRANSITIONS: dict[ProgramStatus, set[ProgramStatus]] = {
    ProgramStatus.PLANNING: {ProgramStatus.ACTIVE, ProgramStatus.ARCHIVED},
    ProgramStatus.ACTIVE: {ProgramStatus.COMPLETED, ProgramStatus.ARCHIVED},
    ProgramStatus.COMPLETED: {ProgramStatus.ARCHIVED},
    ProgramStatus.ARCHIVED: set(),  # Terminal state
}

# Valid status transitions for projects
_VALID_PROJECT_TRANSITIONS: dict[ProjectStatus, set[ProjectStatus]] = {
    ProjectStatus.PLANNING: {ProjectStatus.IN_PROGRESS, ProjectStatus.ON_HOLD},
    ProjectStatus.IN_PROGRESS: {ProjectStatus.COMPLETED, ProjectStatus.ON_HOLD},
    ProjectStatus.ON_HOLD: {ProjectStatus.IN_PROGRESS, ProjectStatus.COMPLETED},
    ProjectStatus.COMPLETED: set(),  # Terminal state
}

# Valid status transitions for activities
_VALID_ACTIVITY_TRANSITIONS: dict[ActivityStatus, set[ActivityStatus]] = {
    ActivityStatus.PENDING: {ActivityStatus.IN_PROGRESS, ActivityStatus.BLOCKED},
    ActivityStatus.IN_PROGRESS: {ActivityStatus.COMPLETED, ActivityStatus.BLOCKED},
    ActivityStatus.BLOCKED: {ActivityStatus.IN_PROGRESS, ActivityStatus.PENDING},
    ActivityStatus.COMPLETED: set(),  # Terminal state
}


def can_transition_program_status(current: ProgramStatus, target: ProgramStatus) -> bool:
    """Return True if the program status transition is allowed."""
    if current == target:
        return True
    return target in _VALID_PROGRAM_TRANSITIONS.get(current, set())


def can_transition_project_status(current: ProjectStatus, target: ProjectStatus) -> bool:
    """Return True if the project status transition is allowed."""
    if current == target:
        return True
    return target in _VALID_PROJECT_TRANSITIONS.get(current, set())


def can_transition_activity_status(current: ActivityStatus, target: ActivityStatus) -> bool:
    """Return True if the activity status transition is allowed."""
    if current == target:
        return True
    return target in _VALID_ACTIVITY_TRANSITIONS.get(current, set())
