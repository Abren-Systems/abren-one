"""Base domain exception hierarchy for Abren One.

All module-level domain exceptions should inherit from :class:`DomainError`
so that the global DRF exception handler can map them to appropriate HTTP
responses automatically.

Convention:
    *NotFoundError  → HTTP 404
    *Error (others) → HTTP 400
"""


class DomainError(Exception):
    """Root exception for all domain errors across every module."""


class NotFoundError(DomainError):
    """Base class for domain-level "not found" errors.

    Subclass this in each module so the global exception handler can map
    them to HTTP 404 without per-view try/except.
    """
