from app.application.interfaces.session_repository import SessionRepository


class LogoutUseCase:
    def __init__(self, session_repository: SessionRepository) -> None:
        self._session_repository = session_repository

    async def execute(self, token: str) -> None:
        await self._session_repository.delete(token)
