from typing import Protocol


class HealthRepository(Protocol):
    async def is_database_connected(self) -> bool: ...
