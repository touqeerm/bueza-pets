from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Session:
    id: int
    user_id: int
    token: str
    created_at: datetime
    expires_at: datetime
