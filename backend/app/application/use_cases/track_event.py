from typing import Any

from app.application.interfaces.event_repository import EventRepository
from app.domain.entities.event import AnalyticsEvent


class TrackEventUseCase:
    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    async def execute(
        self,
        name: str,
        properties: dict[str, Any],
        anonymous_id: str,
        user_id: int | None,
    ) -> AnalyticsEvent:
        return await self._event_repository.create(
            name=name,
            properties=properties,
            anonymous_id=anonymous_id,
            user_id=user_id,
        )
