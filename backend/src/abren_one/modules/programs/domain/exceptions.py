from abren_one.platform.common.exceptions import DomainError, NotFoundError


class ProgramError(DomainError):
    """Base exception for programs domain errors."""


class ProgramNotFoundError(NotFoundError, ProgramError):
    """Raised when a program cannot be found."""


class ProjectNotFoundError(NotFoundError, ProgramError):
    """Raised when a project cannot be found."""


class ActivityNotFoundError(NotFoundError, ProgramError):
    """Raised when an activity cannot be found."""


class InvalidProgramTransitionError(ProgramError):
    """Raised when an invalid program status transition is attempted."""


class InvalidProjectTransitionError(ProgramError):
    """Raised when an invalid project status transition is attempted."""


class InvalidActivityTransitionError(ProgramError):
    """Raised when an invalid activity status transition is attempted."""
