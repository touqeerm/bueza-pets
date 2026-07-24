from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.otp import OtpCode
from app.infrastructure.database.models import OtpCodeModel


class SqlAlchemyOtpRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, phone_number: str, code: str, expires_at: datetime) -> OtpCode:
        model = OtpCodeModel(phone_number=phone_number, code=code, expires_at=expires_at)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_latest_active(self, phone_number: str) -> OtpCode | None:
        result = await self._session.execute(
            select(OtpCodeModel)
            .where(
                OtpCodeModel.phone_number == phone_number,
                OtpCodeModel.consumed_at.is_(None),
                OtpCodeModel.expires_at > datetime.now(timezone.utc),
            )
            .order_by(OtpCodeModel.created_at.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def mark_consumed(self, otp_id: int) -> None:
        model = await self._session.get(OtpCodeModel, otp_id)
        if model is not None:
            model.consumed_at = datetime.now(timezone.utc)
            await self._session.commit()

    @staticmethod
    def _to_entity(model: OtpCodeModel) -> OtpCode:
        return OtpCode(
            id=model.id,
            phone_number=model.phone_number,
            code=model.code,
            expires_at=model.expires_at,
            consumed_at=model.consumed_at,
        )
