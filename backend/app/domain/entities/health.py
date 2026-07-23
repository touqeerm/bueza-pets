from dataclasses import dataclass


@dataclass(frozen=True)
class HealthStatus:
    status: str
    database_connected: bool
