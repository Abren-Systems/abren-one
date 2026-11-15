from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import UUID, uuid4

CORRELATION_HEADER = "X-Correlation-ID"
DJANGO_CORRELATION_HEADER = "HTTP_X_CORRELATION_ID"


class CorrelationMiddleware:
    """Extracts or generates an operational correlation ID for each request (§8.4).

    Reads `X-Correlation-ID` if provided and valid UUID, otherwise generates
    a fresh UUID. Attaches `request.correlation_id` and echoes the header
    in the HTTP response.
    """

    def __init__(self, get_response: Callable[..., Any]) -> None:
        self.get_response = get_response

    def __call__(self, request: Any) -> Any:
        correlation_id = self._extract_or_generate_id(request)
        request.correlation_id = correlation_id

        response = self.get_response(request)

        if hasattr(response, "headers"):
            response.headers[CORRELATION_HEADER] = str(correlation_id)
        elif hasattr(response, "__setitem__"):
            response[CORRELATION_HEADER] = str(correlation_id)

        return response

    def _extract_or_generate_id(self, request: Any) -> UUID:
        raw_id: str | None = None
        if hasattr(request, "headers") and CORRELATION_HEADER in request.headers:
            raw_id = request.headers.get(CORRELATION_HEADER)
        elif hasattr(request, "META") and DJANGO_CORRELATION_HEADER in request.META:
            raw_id = request.META.get(DJANGO_CORRELATION_HEADER)

        if raw_id:
            try:
                return UUID(raw_id.strip())
            except ValueError, AttributeError:
                pass

        return uuid4()
