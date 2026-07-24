from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.domain.errors import InvalidOtpError, InvalidSessionError
from app.infrastructure.database import models  # noqa: F401  registers tables on Base.metadata
from app.infrastructure.database.base import Base
from app.infrastructure.database.session import engine
from app.presentation.api.router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(api_router)


@app.exception_handler(InvalidOtpError)
async def handle_invalid_otp(request: Request, exc: InvalidOtpError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc) or "Invalid or expired OTP code"})


@app.exception_handler(InvalidSessionError)
async def handle_invalid_session(request: Request, exc: InvalidSessionError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc) or "Invalid or expired session"})
