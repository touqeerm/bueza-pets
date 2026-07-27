from app.application.interfaces.journal_entry_repository import JournalEntryRepository
from app.domain.entities.journal_entry import JournalEntry, JournalEntryType


class ListJournalEntriesUseCase:
    def __init__(self, journal_entry_repository: JournalEntryRepository) -> None:
        self._journal_entry_repository = journal_entry_repository

    async def execute(
        self,
        experiment_id: int | None = None,
        entry_type: JournalEntryType | None = None,
        limit: int = 50,
    ) -> list[JournalEntry]:
        return await self._journal_entry_repository.list_all(experiment_id, entry_type, limit)
