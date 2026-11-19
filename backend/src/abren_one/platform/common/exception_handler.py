"""Global DRF exception handler for domain errors.

Maps the ``DomainError`` hierarchy to appropriate HTTP responses so that
views do not need per-method try/except boilerplate:

    *NotFoundError  → HTTP 404  (DRF ``NotFound``)
    *DomainError    → HTTP 400  (DRF ``ValidationError``)

Non-domain exceptions fall through to DRF's default handler.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import exceptions as drf_exceptions
from rest_framework.views import exception_handler as drf_default_handler

from abren_one.platform.common.exceptions import DomainError, NotFoundError

if TYPE_CHECKING:
    from rest_framework.response import Response

logger = logging.getLogger(__name__)


def handle_domain_exception(exc: Exception, context: dict) -> Response | None:
    """Custom DRF exception handler.

    1. If the exception is a :class:`NotFoundError`, convert to DRF ``NotFound``.
    2. If the exception is a :class:`DomainError`, convert to DRF ``ValidationError``.
    3. Otherwise, delegate to DRF's default handler.
    """
    if isinstance(exc, NotFoundError):
        drf_exc = drf_exceptions.NotFound(detail=str(exc))
        drf_exc.__cause__ = exc
        return drf_default_handler(drf_exc, context)

    if isinstance(exc, DomainError):
        drf_exc = drf_exceptions.ValidationError(detail={"error": str(exc)})
        drf_exc.__cause__ = exc
        return drf_default_handler(drf_exc, context)

    return drf_default_handler(exc, context)
