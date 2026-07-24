from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.check_health import CheckHealthUseCase
from app.application.use_cases.get_current_user import GetCurrentUserUseCase
from app.application.use_cases.logout import LogoutUseCase
from app.application.use_cases.request_otp import RequestOtpUseCase
from app.application.use_cases.track_event import TrackEventUseCase
from app.application.use_cases.verify_otp import VerifyOtpUseCase
from app.domain.entities.user import User
from app.infrastructure.database.session import get_session
from app.infrastructure.repositories.event_repository import SqlAlchemyEventRepository
from app.infrastructure.repositories.health_repository import SqlAlchemyHealthRepository
from app.infrastructure.repositories.otp_repository import SqlAlchemyOtpRepository
from app.infrastructure.repositories.session_repository import SqlAlchemySessionRepository
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository

bearer_scheme = HTTPBearer()


def get_check_health_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CheckHealthUseCase:
    repository = SqlAlchemyHealthRepository(session)
    return CheckHealthUseCase(repository)


def get_request_otp_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RequestOtpUseCase:
    return RequestOtpUseCase(SqlAlchemyOtpRepository(session))


def get_verify_otp_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> VerifyOtpUseCase:
    return VerifyOtpUseCase(
        otp_repository=SqlAlchemyOtpRepository(session),
        user_repository=SqlAlchemyUserRepository(session),
        session_repository=SqlAlchemySessionRepository(session),
    )


def get_logout_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LogoutUseCase:
    return LogoutUseCase(SqlAlchemySessionRepository(session))


def get_current_user_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(
        session_repository=SqlAlchemySessionRepository(session),
        user_repository=SqlAlchemyUserRepository(session),
    )


def get_track_event_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TrackEventUseCase:
    return TrackEventUseCase(SqlAlchemyEventRepository(session))


async def get_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> str:
    return credentials.credentials


async def get_current_user(
    token: Annotated[str, Depends(get_bearer_token)],
    use_case: Annotated[GetCurrentUserUseCase, Depends(get_current_user_use_case)],
) -> User:
    return await use_case.execute(token)
