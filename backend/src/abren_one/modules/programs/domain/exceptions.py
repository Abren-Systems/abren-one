from abren_one.platform.common.exceptions import DomainError, NotFoundError


class ProgramError(DomainError):
    """Base exception for programs domain errors."""


class ProgramNotFoundError(NotFoundError, ProgramError):
    """Raised when a program cannot be found."""


class ProjectNotFoundError(NotFoundError, ProgramError):
    """Raised when a project cannot be found."""
