from typing import Any

from pydantic import BaseModel, Field

from app.domain.events import EventName


class TrackEventRequest(BaseModel):
    event_name: EventName
    properties: dict[str, Any] = Field(default_factory=dict)
    anonymous_id: str = Field(min_length=1, max_length=64)
    user_id: int | None = None


class TrackEventResponse(BaseModel):
    id: int
    event_name: str
