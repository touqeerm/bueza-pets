from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.check_health import CheckHealthUseCase
from app.infrastructure.database.session import get_session
from app.infrastructure.repositories.health_repository import SqlAlchemyHealthRepository


def get_check_health_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CheckHealthUseCase:
    repository = SqlAlchemyHealthRepository(session)
    return CheckHealthUseCase(repository)
