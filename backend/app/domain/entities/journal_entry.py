from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class JournalEntryType(StrEnum):
    OBSERVATION = "observation"
    DECISION = "decision"
    PIVOT_CONSIDERATION = "pivot_consideration"
    NOTE = "note"


@dataclass(frozen=True)
class JournalEntry:
    id: int
    experiment_id: int | None
    entry_type: JournalEntryType
    body: str
    created_by_user_id: int | None
    created_at: datetime
