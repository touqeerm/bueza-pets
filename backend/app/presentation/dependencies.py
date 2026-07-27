from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.add_journal_entry import AddJournalEntryUseCase
from app.application.use_cases.add_metric import AddMetricUseCase
from app.application.use_cases.archive_experiment import ArchiveExperimentUseCase
from app.application.use_cases.create_experiment import CreateExperimentUseCase
from app.application.use_cases.evaluate_experiment import EvaluateExperimentUseCase
from app.application.use_cases.get_current_user import GetCurrentUserUseCase
from app.application.use_cases.get_dashboard_snapshot import GetDashboardSnapshotUseCase
from app.application.use_cases.get_evaluation_history import GetEvaluationHistoryUseCase
from app.application.use_cases.get_experiment_detail import GetExperimentDetailUseCase
from app.application.use_cases.list_experiments import ListExperimentsUseCase
from app.application.use_cases.list_journal_entries import ListJournalEntriesUseCase
from app.application.use_cases.logout import LogoutUseCase
from app.application.use_cases.remove_metric import RemoveMetricUseCase
from app.application.use_cases.request_otp import RequestOtpUseCase
from app.application.use_cases.start_experiment import StartExperimentUseCase
from app.application.use_cases.track_event import TrackEventUseCase
from app.application.use_cases.update_experiment import UpdateExperimentUseCase
from app.application.use_cases.verify_otp import VerifyOtpUseCase
from app.domain.entities.user import User
from app.domain.errors import AdminAccessRequiredError
from app.infrastructure.database.session import get_session
from app.infrastructure.repositories.evaluation_run_repository import SqlAlchemyEvaluationRunRepository
from app.infrastructure.repositories.event_repository import SqlAlchemyEventRepository
from app.infrastructure.repositories.experiment_repository import SqlAlchemyExperimentRepository
from app.infrastructure.repositories.journal_entry_repository import SqlAlchemyJournalEntryRepository
from app.infrastructure.repositories.metric_repository import SqlAlchemyMetricRepository
from app.infrastructure.repositories.otp_repository import SqlAlchemyOtpRepository
from app.infrastructure.repositories.session_repository import SqlAlchemySessionRepository
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository

bearer_scheme = HTTPBearer()


def get_request_otp_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RequestOtpUseCase:
    return RequestOtpUseCase(SqlAlchemyOtpRepository(session))


def get_verify_otp_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> VerifyOtpUseCase:
    return VerifyOtpUseCase(
        otp_repository=SqlAlchemyOtpRepository(session),
        user_repository=SqlAlchemyUserRepository(session),
        session_repository=SqlAlchemySessionRepository(session),
    )


def get_logout_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LogoutUseCase:
    return LogoutUseCase(SqlAlchemySessionRepository(session))


def get_current_user_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(
        session_repository=SqlAlchemySessionRepository(session),
        user_repository=SqlAlchemyUserRepository(session),
    )


def get_track_event_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TrackEventUseCase:
    return TrackEventUseCase(SqlAlchemyEventRepository(session))


async def get_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> str:
    return credentials.credentials


async def get_current_user(
    token: Annotated[str, Depends(get_bearer_token)],
    use_case: Annotated[GetCurrentUserUseCase, Depends(get_current_user_use_case)],
) -> User:
    return await use_case.execute(token)


async def require_admin_user(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.is_admin:
        raise AdminAccessRequiredError()
    return user


# ---- Experimentation platform (Tier 1) ----


def get_create_experiment_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateExperimentUseCase:
    return CreateExperimentUseCase(SqlAlchemyExperimentRepository(session))


def get_update_experiment_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UpdateExperimentUseCase:
    return UpdateExperimentUseCase(SqlAlchemyExperimentRepository(session))


def get_add_metric_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AddMetricUseCase:
    return AddMetricUseCase(SqlAlchemyExperimentRepository(session), SqlAlchemyMetricRepository(session))


def get_remove_metric_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RemoveMetricUseCase:
    return RemoveMetricUseCase(SqlAlchemyExperimentRepository(session), SqlAlchemyMetricRepository(session))


def get_start_experiment_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> StartExperimentUseCase:
    return StartExperimentUseCase(SqlAlchemyExperimentRepository(session), SqlAlchemyMetricRepository(session))


def get_archive_experiment_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ArchiveExperimentUseCase:
    return ArchiveExperimentUseCase(SqlAlchemyExperimentRepository(session))


def get_evaluate_experiment_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EvaluateExperimentUseCase:
    return EvaluateExperimentUseCase(
        experiment_repository=SqlAlchemyExperimentRepository(session),
        metric_repository=SqlAlchemyMetricRepository(session),
        event_repository=SqlAlchemyEventRepository(session),
        evaluation_run_repository=SqlAlchemyEvaluationRunRepository(session),
    )


def get_add_journal_entry_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AddJournalEntryUseCase:
    return AddJournalEntryUseCase(SqlAlchemyJournalEntryRepository(session))


def get_dashboard_snapshot_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetDashboardSnapshotUseCase:
    return GetDashboardSnapshotUseCase(
        experiment_repository=SqlAlchemyExperimentRepository(session),
        metric_repository=SqlAlchemyMetricRepository(session),
        evaluation_run_repository=SqlAlchemyEvaluationRunRepository(session),
        journal_entry_repository=SqlAlchemyJournalEntryRepository(session),
    )


def get_list_experiments_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListExperimentsUseCase:
    return ListExperimentsUseCase(SqlAlchemyExperimentRepository(session))


def get_experiment_detail_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetExperimentDetailUseCase:
    return GetExperimentDetailUseCase(
        experiment_repository=SqlAlchemyExperimentRepository(session),
        metric_repository=SqlAlchemyMetricRepository(session),
        evaluation_run_repository=SqlAlchemyEvaluationRunRepository(session),
    )


def get_list_journal_entries_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ListJournalEntriesUseCase:
    return ListJournalEntriesUseCase(SqlAlchemyJournalEntryRepository(session))


def get_evaluation_history_use_case(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> GetEvaluationHistoryUseCase:
    return GetEvaluationHistoryUseCase(SqlAlchemyEvaluationRunRepository(session))
