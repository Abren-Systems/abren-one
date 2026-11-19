"""Health check views for operational readiness probes."""

from django.db import connection
from django.http import JsonResponse


def health(request):
    """Lightweight liveness probe — always returns 200 if the process is up."""
    return JsonResponse({"status": "ok"})


def ready(request):
    """Readiness probe — verifies the database connection is working."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ready"})
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)
