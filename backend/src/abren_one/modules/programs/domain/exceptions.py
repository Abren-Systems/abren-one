class ProgramError(Exception):
    """Base exception for programs domain errors."""


class ProgramNotFoundError(ProgramError):
    """Raised when a program cannot be found."""


class ProjectNotFoundError(ProgramError):
    """Raised when a project cannot be found."""
