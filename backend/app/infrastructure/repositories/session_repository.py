from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.session import Session
from app.infrastructure.database.models import SessionModel


class SqlAlchemySessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_id: int, token: str, expires_at: datetime) -> Session:
        model = SessionModel(user_id=user_id, token=token, expires_at=expires_at)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_token(self, token: str) -> Session | None:
        result = await self._session.execute(select(SessionModel).where(SessionModel.token == token))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def delete(self, token: str) -> None:
        await self._session.execute(delete(SessionModel).where(SessionModel.token == token))
        await self._session.commit()

    @staticmethod
    def _to_entity(model: SessionModel) -> Session:
        return Session(
            id=model.id,
            user_id=model.user_id,
            token=model.token,
            created_at=model.created_at,
            expires_at=model.expires_at,
        )
