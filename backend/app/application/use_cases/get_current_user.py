from datetime import datetime, timezone

from app.application.interfaces.session_repository import SessionRepository
from app.application.interfaces.user_repository import UserRepository
from app.domain.entities.user import User
from app.domain.errors import InvalidSessionError


class GetCurrentUserUseCase:
    def __init__(self, session_repository: SessionRepository, user_repository: UserRepository) -> None:
        self._session_repository = session_repository
        self._user_repository = user_repository

    async def execute(self, token: str) -> User:
        session = await self._session_repository.get_by_token(token)
        if session is None or session.expires_at < datetime.now(timezone.utc):
            raise InvalidSessionError("Invalid or expired session")

        user = await self._user_repository.get_by_id(session.user_id)
        if user is None:
            raise InvalidSessionError("Invalid or expired session")

        return user
