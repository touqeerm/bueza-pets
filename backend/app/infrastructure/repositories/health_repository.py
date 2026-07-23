from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyHealthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def is_database_connected(self) -> bool:
        try:
            await self._session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
