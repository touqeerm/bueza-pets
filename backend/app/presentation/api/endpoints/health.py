from typing import Annotated

from fastapi import APIRouter, Depends

from app.application.use_cases.check_health import CheckHealthUseCase
from app.presentation.dependencies import get_check_health_use_case
from app.presentation.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def get_health(
    use_case: Annotated[CheckHealthUseCase, Depends(get_check_health_use_case)],
) -> HealthResponse:
    result = await use_case.execute()
    return HealthResponse(status=result.status, database_connected=result.database_connected)
