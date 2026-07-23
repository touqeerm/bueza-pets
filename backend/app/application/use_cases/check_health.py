from app.application.interfaces.health_repository import HealthRepository
from app.domain.entities.health import HealthStatus


class CheckHealthUseCase:
    def __init__(self, health_repository: HealthRepository) -> None:
        self._health_repository = health_repository

    async def execute(self) -> HealthStatus:
        database_connected = await self._health_repository.is_database_connected()
        status = "ok" if database_connected else "degraded"
        return HealthStatus(status=status, database_connected=database_connected)
