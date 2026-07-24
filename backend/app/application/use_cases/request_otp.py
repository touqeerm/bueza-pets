import secrets
from datetime import datetime, timedelta, timezone

from app.application.interfaces.otp_repository import OtpRepository
from app.domain.entities.otp import OtpCode

OTP_TTL_SECONDS = 300


class RequestOtpUseCase:
    def __init__(self, otp_repository: OtpRepository) -> None:
        self._otp_repository = otp_repository

    async def execute(self, phone_number: str) -> OtpCode:
        code = f"{secrets.randbelow(1_000_000):06d}"
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=OTP_TTL_SECONDS)
        return await self._otp_repository.create(phone_number, code, expires_at)
