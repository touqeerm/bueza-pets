from datetime import datetime
from typing import Protocol

from app.domain.entities.session import Session


class SessionRepository(Protocol):
    async def create(self, user_id: int, token: str, expires_at: datetime) -> Session: ...
    async def get_by_token(self, token: str) -> Session | None: ...
    async def delete(self, token: str) -> None: ...
