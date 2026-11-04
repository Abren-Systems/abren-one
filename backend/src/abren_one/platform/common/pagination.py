"""Pagination classes for Abren One APIs."""

from rest_framework.pagination import CursorPagination


class StandardCursorPagination(CursorPagination):
    """Default cursor pagination ordered by created_at descending."""

    page_size = 50
    ordering = "-created_at"
