"""Document number generation service for Finance."""

from datetime import date
from uuid import UUID

from abren_one.modules.finance.models.journal_entry import JournalEntry


def generate_journal_entry_number(organization_id: UUID, entry_date: date) -> str:
    """Generate a sequential entry number for the year with concurrency locking, e.g. JE-2026-0001.

    Locks the existing entries for the organization and year within an active transaction
    to serialize concurrent number generation without race conditions.
    """
    year = entry_date.year
    prefix = f"JE-{year}-"
    last_entry = (
        JournalEntry.objects.select_for_update()
        .filter(
            organization_id=organization_id,
            entry_number__startswith=prefix,
        )
        .order_by("-entry_number")
        .first()
    )
    next_seq = 1
    if last_entry:
        try:
            seq_part = last_entry.entry_number.split("-")[-1]
            next_seq = int(seq_part) + 1
        except ValueError, IndexError:
            next_seq = 1
    return f"{prefix}{next_seq:04d}"
