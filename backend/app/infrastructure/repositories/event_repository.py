from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.event import AnalyticsEvent
from app.infrastructure.database.models import EventModel


class SqlAlchemyEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        name: str,
        properties: dict[str, Any],
        anonymous_id: str,
        user_id: int | None,
    ) -> AnalyticsEvent:
        model = EventModel(name=name, properties=properties, anonymous_id=anonymous_id, user_id=user_id)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: EventModel) -> AnalyticsEvent:
        return AnalyticsEvent(
            id=model.id,
            name=model.name,
            properties=model.properties,
            anonymous_id=model.anonymous_id,
            user_id=model.user_id,
            created_at=model.created_at,
        )
