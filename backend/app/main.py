import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.application.use_cases.evaluate_experiment import EvaluateExperimentUseCase
from app.core.config import get_settings
from app.domain.entities.experiment import ExperimentStatus
from app.domain.errors import (
    AdminAccessRequiredError,
    ExperimentNotEvaluableError,
    InvalidExperimentTransitionError,
    InvalidOtpError,
    InvalidSessionError,
)
from app.infrastructure.database import models  # noqa: F401  registers tables on Base.metadata
from app.infrastructure.database.base import Base
from app.infrastructure.database.session import AsyncSessionLocal, engine
from app.infrastructure.repositories.evaluation_run_repository import SqlAlchemyEvaluationRunRepository
from app.infrastructure.repositories.event_repository import SqlAlchemyEventRepository
from app.infrastructure.repositories.experiment_repository import SqlAlchemyExperimentRepository
from app.infrastructure.repositories.metric_repository import SqlAlchemyMetricRepository
from app.presentation.api.router import api_router

settings = get_settings()
logger = logging.getLogger(__name__)

# How often the Evaluation Engine re-checks every running/evaluating
# experiment. In-process asyncio loop rather than Celery+Redis or an external
# cron container — this project has neither, and a single-developer,
# low-traffic app doesn't need them yet (YAGNI). A manual "evaluate now"
# endpoint (POST /admin/experiments/{id}/evaluate) covers the case where a
# founder doesn't want to wait for the next tick.
EVALUATION_INTERVAL_SECONDS = 15 * 60


async def _run_evaluation_cycle() -> None:
    async with AsyncSessionLocal() as session:
        experiment_repository = SqlAlchemyExperimentRepository(session)
        use_case = EvaluateExperimentUseCase(
            experiment_repository=experiment_repository,
            metric_repository=SqlAlchemyMetricRepository(session),
            event_repository=SqlAlchemyEventRepository(session),
            evaluation_run_repository=SqlAlchemyEvaluationRunRepository(session),
        )
        experiments = await experiment_repository.list_all(ExperimentStatus.RUNNING)
        experiments += await experiment_repository.list_all(ExperimentStatus.EVALUATING)
        for experiment in experiments:
            try:
                await use_case.execute(experiment.id)
            except ExperimentNotEvaluableError:
                continue
            except Exception:
                logger.exception("Evaluation cycle failed for experiment %s", experiment.id)


async def _evaluation_loop() -> None:
    while True:
        await asyncio.sleep(EVALUATION_INTERVAL_SECONDS)
        await _run_evaluation_cycle()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    evaluation_task = asyncio.create_task(_evaluation_loop())
    yield
    evaluation_task.cancel()
    await engine.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(api_router)


@app.exception_handler(InvalidOtpError)
async def handle_invalid_otp(request: Request, exc: InvalidOtpError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc) or "Invalid or expired OTP code"})


@app.exception_handler(InvalidSessionError)
async def handle_invalid_session(request: Request, exc: InvalidSessionError) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": str(exc) or "Invalid or expired session"})


@app.exception_handler(AdminAccessRequiredError)
async def handle_admin_access_required(request: Request, exc: AdminAccessRequiredError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": "Admin access required"})


@app.exception_handler(InvalidExperimentTransitionError)
async def handle_invalid_experiment_transition(request: Request, exc: InvalidExperimentTransitionError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(ExperimentNotEvaluableError)
async def handle_experiment_not_evaluable(request: Request, exc: ExperimentNotEvaluableError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})
