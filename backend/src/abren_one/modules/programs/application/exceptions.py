"""Application-level exceptions for the Programs module (§2.2)."""

from abren_one.modules.programs.domain.exceptions import (
    ActivityNotFoundError,
    InvalidActivityTransitionError,
    InvalidProgramTransitionError,
    InvalidProjectTransitionError,
    ProgramError,
    ProgramNotFoundError,
    ProjectNotFoundError,
)

__all__ = [
    "ActivityNotFoundError",
    "InvalidActivityTransitionError",
    "InvalidProgramTransitionError",
    "InvalidProjectTransitionError",
    "ProgramError",
    "ProgramNotFoundError",
    "ProjectNotFoundError",
]
