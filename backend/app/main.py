from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.infrastructure.database.session import engine
from app.presentation.api.router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(api_router)
