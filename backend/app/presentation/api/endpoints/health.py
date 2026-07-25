from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_session
from app.presentation.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def get_health(session: Annotated[AsyncSession, Depends(get_session)]) -> HealthResponse:
    try:
        await session.execute(text("SELECT 1"))
        database_connected = True
    except Exception:
        database_connected = False

    return HealthResponse(
        status="ok" if database_connected else "degraded",
        database_connected=database_connected,
    )
