from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    database_connected: bool
