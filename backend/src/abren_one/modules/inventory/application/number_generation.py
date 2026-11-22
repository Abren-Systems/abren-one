"""Document number generation service for Inventory."""

from typing import Any
from uuid import UUID

from django.utils import timezone


def generate_document_number(organization_id: UUID, prefix: str, model_class: Any) -> str:
    """Generate the next sequential document number within a transaction.

    Locks the existing rows for the organization to serialize concurrent sequence queries.
    Format: {PREFIX}-{YYYYMM}-{NNNN}
    """
    year_month = timezone.now().strftime("%Y%m")
    prefix_pattern = f"{prefix}-{year_month}-"

    last = (
        model_class.objects.select_for_update()
        .filter(organization_id=organization_id)
        .filter(**{f"{model_class.NUMBER_FIELD}__startswith": prefix_pattern})
        .order_by(f"-{model_class.NUMBER_FIELD}")
        .first()
    )

    if last:
        val = getattr(last, model_class.NUMBER_FIELD)
        try:
            seq = int(val.split("-")[-1]) + 1
        except ValueError, IndexError:
            seq = 1
    else:
        seq = 1

    return f"{prefix_pattern}{seq:04d}"
