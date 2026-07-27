from app.application.interfaces.journal_entry_repository import JournalEntryRepository
from app.domain.entities.journal_entry import JournalEntry, JournalEntryType


class AddJournalEntryUseCase:
    def __init__(self, journal_entry_repository: JournalEntryRepository) -> None:
        self._journal_entry_repository = journal_entry_repository

    async def execute(
        self,
        entry_type: JournalEntryType,
        body: str,
        experiment_id: int | None,
        created_by_user_id: int | None,
    ) -> JournalEntry:
        return await self._journal_entry_repository.create(
            entry_type=entry_type,
            body=body,
            experiment_id=experiment_id,
            created_by_user_id=created_by_user_id,
        )
