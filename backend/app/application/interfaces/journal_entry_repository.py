from typing import Protocol

from app.domain.entities.journal_entry import JournalEntry, JournalEntryType


class JournalEntryRepository(Protocol):
    async def create(
        self,
        entry_type: JournalEntryType,
        body: str,
        experiment_id: int | None,
        created_by_user_id: int | None,
    ) -> JournalEntry: ...

    async def list_all(
        self,
        experiment_id: int | None = None,
        entry_type: JournalEntryType | None = None,
        limit: int = 50,
    ) -> list[JournalEntry]: ...
