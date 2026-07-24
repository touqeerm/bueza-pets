from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class AnalyticsEvent:
    id: int
    name: str
    properties: dict[str, Any]
    anonymous_id: str
    user_id: int | None
    created_at: datetime
