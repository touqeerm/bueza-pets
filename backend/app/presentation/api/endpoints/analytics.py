from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.use_cases.track_event import TrackEventUseCase
from app.presentation.dependencies import get_track_event_use_case
from app.presentation.schemas.analytics import TrackEventRequest, TrackEventResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/events", response_model=TrackEventResponse, status_code=201)
async def track_event(
    payload: TrackEventRequest,
    use_case: Annotated[TrackEventUseCase, Depends(get_track_event_use_case)],
) -> TrackEventResponse:
    event = await use_case.execute(
        name=payload.event_name.value,
        properties=payload.properties,
        anonymous_id=payload.anonymous_id,
        user_id=payload.user_id,
    )
    return TrackEventResponse(id=event.id, event_name=event.name)
