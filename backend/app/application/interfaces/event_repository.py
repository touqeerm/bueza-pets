from typing import Any, Protocol

from app.domain.entities.event import AnalyticsEvent


class EventRepository(Protocol):
    async def create(
        self,
        name: str,
        properties: dict[str, Any],
        anonymous_id: str,
        user_id: int | None,
    ) -> AnalyticsEvent: ...
