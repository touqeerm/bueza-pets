import secrets
from datetime import datetime, timedelta, timezone

from app.application.interfaces.otp_repository import OtpRepository
from app.application.interfaces.session_repository import SessionRepository
from app.application.interfaces.user_repository import UserRepository
from app.domain.entities.session import Session
from app.domain.entities.user import User
from app.domain.errors import InvalidOtpError

SESSION_TTL_SECONDS = 60 * 60 * 24 * 30


class VerifyOtpUseCase:
    def __init__(
        self,
        otp_repository: OtpRepository,
        user_repository: UserRepository,
        session_repository: SessionRepository,
    ) -> None:
        self._otp_repository = otp_repository
        self._user_repository = user_repository
        self._session_repository = session_repository

    async def execute(self, phone_number: str, code: str) -> tuple[User, Session]:
        otp = await self._otp_repository.get_latest_active(phone_number)
        if otp is None or otp.code != code:
            raise InvalidOtpError("Invalid or expired OTP code")

        await self._otp_repository.mark_consumed(otp.id)

        user = await self._user_repository.get_by_phone_number(phone_number)
        if user is None:
            user = await self._user_repository.create(phone_number)

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=SESSION_TTL_SECONDS)
        session = await self._session_repository.create(user.id, token, expires_at)

        return user, session
