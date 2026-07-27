from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    id: int
    phone_number: str
    is_admin: bool
    created_at: datetime
