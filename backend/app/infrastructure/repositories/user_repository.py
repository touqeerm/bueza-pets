from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.infrastructure.database.models import UserModel


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_phone_number(self, phone_number: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.phone_number == phone_number))
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_id(self, user_id: int) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return self._to_entity(model) if model else None

    async def create(self, phone_number: str) -> User:
        model = UserModel(phone_number=phone_number)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(id=model.id, phone_number=model.phone_number, created_at=model.created_at)
