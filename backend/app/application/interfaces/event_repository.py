from datetime import datetime
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

    async def count_distinct_actors(
        self,
        event_name: str,
        since: datetime,
        property_filters: dict[str, Any],
    ) -> int:
        """Count distinct users/anonymous visitors who fired this event since `since`.

        Dedupes on user_id where present, falling back to anonymous_id, so a
        farmer who fires the same event once logged-in and once anonymously
        (pre/post-login) isn't double-counted.
        """
        ...
