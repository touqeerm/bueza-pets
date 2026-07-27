from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.journal_entry import JournalEntry, JournalEntryType
from app.infrastructure.database.models import JournalEntryModel


class SqlAlchemyJournalEntryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        entry_type: JournalEntryType,
        body: str,
        experiment_id: int | None,
        created_by_user_id: int | None,
    ) -> JournalEntry:
        model = JournalEntryModel(
            entry_type=entry_type.value,
            body=body,
            experiment_id=experiment_id,
            created_by_user_id=created_by_user_id,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def list_all(
        self,
        experiment_id: int | None = None,
        entry_type: JournalEntryType | None = None,
        limit: int = 50,
    ) -> list[JournalEntry]:
        query = select(JournalEntryModel).order_by(JournalEntryModel.created_at.desc()).limit(limit)
        if experiment_id is not None:
            query = query.where(JournalEntryModel.experiment_id == experiment_id)
        if entry_type is not None:
            query = query.where(JournalEntryModel.entry_type == entry_type.value)
        result = await self._session.execute(query)
        return [self._to_entity(model) for model in result.scalars().all()]

    @staticmethod
    def _to_entity(model: JournalEntryModel) -> JournalEntry:
        return JournalEntry(
            id=model.id,
            experiment_id=model.experiment_id,
            entry_type=JournalEntryType(model.entry_type),
            body=model.body,
            created_by_user_id=model.created_by_user_id,
            created_at=model.created_at,
        )
