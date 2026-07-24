from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class OtpCode:
    id: int
    phone_number: str
    code: str
    expires_at: datetime
    consumed_at: datetime | None
