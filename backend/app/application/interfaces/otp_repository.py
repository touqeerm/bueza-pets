from datetime import datetime
from typing import Protocol

from app.domain.entities.otp import OtpCode


class OtpRepository(Protocol):
    async def create(self, phone_number: str, code: str, expires_at: datetime) -> OtpCode: ...
    async def get_latest_active(self, phone_number: str) -> OtpCode | None: ...
    async def mark_consumed(self, otp_id: int) -> None: ...
