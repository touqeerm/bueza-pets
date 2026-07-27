from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.application.use_cases.add_journal_entry import AddJournalEntryUseCase
from app.application.use_cases.add_metric import AddMetricUseCase
from app.application.use_cases.archive_experiment import ArchiveExperimentUseCase
from app.application.use_cases.create_experiment import CreateExperimentUseCase
from app.application.use_cases.evaluate_experiment import EvaluateExperimentUseCase
from app.application.use_cases.get_dashboard_snapshot import (
    DashboardSnapshot,
    ExperimentSnapshot,
    GetDashboardSnapshotUseCase,
)
from app.application.use_cases.get_evaluation_history import GetEvaluationHistoryUseCase
from app.application.use_cases.get_experiment_detail import GetExperimentDetailUseCase
from app.application.use_cases.list_experiments import ListExperimentsUseCase
from app.application.use_cases.list_journal_entries import ListJournalEntriesUseCase
from app.application.use_cases.remove_metric import RemoveMetricUseCase
from app.application.use_cases.start_experiment import StartExperimentUseCase
from app.application.use_cases.update_experiment import UpdateExperimentUseCase
from app.domain.entities.experiment import ExperimentStatus, Hypothesis
from app.domain.entities.user import User
from app.presentation.dependencies import (
    get_add_journal_entry_use_case,
    get_add_metric_use_case,
    get_archive_experiment_use_case,
    get_create_experiment_use_case,
    get_dashboard_snapshot_use_case,
    get_evaluate_experiment_use_case,
    get_evaluation_history_use_case,
    get_experiment_detail_use_case,
    get_list_experiments_use_case,
    get_list_journal_entries_use_case,
    get_remove_metric_use_case,
    get_start_experiment_use_case,
    get_update_experiment_use_case,
    require_admin_user,
)
from app.presentation.schemas.admin import (
    DashboardResponse,
    EvaluationRunResponse,
    ExperimentCreateRequest,
    ExperimentResponse,
    ExperimentUpdateRequest,
    JournalEntryCreateRequest,
    JournalEntryResponse,
    MetricCreateRequest,
    MetricResponse,
)

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin_user)])


def _experiment_response_from_snapshot(snapshot: ExperimentSnapshot) -> ExperimentResponse:
    metrics = [MetricResponse.from_domain(m.metric, m.latest_run) for m in snapshot.metrics]
    return ExperimentResponse.from_domain(snapshot.experiment, metrics)


@router.post("/experiments", response_model=ExperimentResponse, status_code=201)
async def create_experiment(
    payload: ExperimentCreateRequest,
    user: Annotated[User, Depends(require_admin_user)],
    use_case: Annotated[CreateExperimentUseCase, Depends(get_create_experiment_use_case)],
) -> ExperimentResponse:
    experiment = await use_case.execute(
        title=payload.title,
        hypothesis=Hypothesis(**payload.hypothesis.model_dump()),
        evaluation_window_days=payload.evaluation_window_days,
        created_by_user_id=user.id,
    )
    return ExperimentResponse.from_domain(experiment)


@router.get("/experiments", response_model=list[ExperimentResponse])
async def list_experiments(
    use_case: Annotated[ListExperimentsUseCase, Depends(get_list_experiments_use_case)],
    status: ExperimentStatus | None = None,
) -> list[ExperimentResponse]:
    experiments = await use_case.execute(status)
    return [ExperimentResponse.from_domain(experiment) for experiment in experiments]


@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(
    experiment_id: int,
    use_case: Annotated[GetExperimentDetailUseCase, Depends(get_experiment_detail_use_case)],
) -> ExperimentResponse:
    snapshot = await use_case.execute(experiment_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return _experiment_response_from_snapshot(snapshot)


@router.patch("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def update_experiment(
    experiment_id: int,
    payload: ExperimentUpdateRequest,
    use_case: Annotated[UpdateExperimentUseCase, Depends(get_update_experiment_use_case)],
) -> ExperimentResponse:
    experiment = await use_case.execute(
        experiment_id=experiment_id,
        title=payload.title,
        hypothesis=Hypothesis(**payload.hypothesis.model_dump()),
        evaluation_window_days=payload.evaluation_window_days,
    )
    return ExperimentResponse.from_domain(experiment)


@router.post("/experiments/{experiment_id}/metrics", response_model=MetricResponse, status_code=201)
async def add_metric(
    experiment_id: int,
    payload: MetricCreateRequest,
    use_case: Annotated[AddMetricUseCase, Depends(get_add_metric_use_case)],
) -> MetricResponse:
    metric = await use_case.execute(
        experiment_id=experiment_id,
        name=payload.name,
        kind=payload.kind,
        is_guardrail=payload.is_guardrail,
        target_value=payload.target_value,
        minimum_sample_size=payload.minimum_sample_size,
        event_mappings=[
            (mapping.role, mapping.event_name.value, mapping.property_filters) for mapping in payload.event_mappings
        ],
    )
    return MetricResponse.from_domain(metric)


@router.delete("/experiments/{experiment_id}/metrics/{metric_id}", status_code=204)
async def remove_metric(
    experiment_id: int,
    metric_id: int,
    use_case: Annotated[RemoveMetricUseCase, Depends(get_remove_metric_use_case)],
) -> None:
    await use_case.execute(experiment_id, metric_id)


@router.post("/experiments/{experiment_id}/start", response_model=ExperimentResponse)
async def start_experiment(
    experiment_id: int,
    use_case: Annotated[StartExperimentUseCase, Depends(get_start_experiment_use_case)],
) -> ExperimentResponse:
    experiment = await use_case.execute(experiment_id)
    return ExperimentResponse.from_domain(experiment)


@router.post("/experiments/{experiment_id}/evaluate", response_model=ExperimentResponse)
async def evaluate_experiment(
    experiment_id: int,
    use_case: Annotated[EvaluateExperimentUseCase, Depends(get_evaluate_experiment_use_case)],
) -> ExperimentResponse:
    experiment = await use_case.execute(experiment_id)
    return ExperimentResponse.from_domain(experiment)


@router.post("/experiments/{experiment_id}/archive", response_model=ExperimentResponse)
async def archive_experiment(
    experiment_id: int,
    use_case: Annotated[ArchiveExperimentUseCase, Depends(get_archive_experiment_use_case)],
) -> ExperimentResponse:
    experiment = await use_case.execute(experiment_id)
    return ExperimentResponse.from_domain(experiment)


@router.get("/experiments/{experiment_id}/evaluation-runs", response_model=list[EvaluationRunResponse])
async def get_evaluation_runs(
    metric_id: int,
    use_case: Annotated[GetEvaluationHistoryUseCase, Depends(get_evaluation_history_use_case)],
) -> list[EvaluationRunResponse]:
    runs = await use_case.execute(metric_id)
    return [EvaluationRunResponse.from_domain(run) for run in runs]


@router.post("/journal-entries", response_model=JournalEntryResponse, status_code=201)
async def add_journal_entry(
    payload: JournalEntryCreateRequest,
    user: Annotated[User, Depends(require_admin_user)],
    use_case: Annotated[AddJournalEntryUseCase, Depends(get_add_journal_entry_use_case)],
) -> JournalEntryResponse:
    entry = await use_case.execute(
        entry_type=payload.entry_type,
        body=payload.body,
        experiment_id=payload.experiment_id,
        created_by_user_id=user.id,
    )
    return JournalEntryResponse.from_domain(entry)


@router.get("/journal-entries", response_model=list[JournalEntryResponse])
async def list_journal_entries(
    use_case: Annotated[ListJournalEntriesUseCase, Depends(get_list_journal_entries_use_case)],
    experiment_id: int | None = None,
) -> list[JournalEntryResponse]:
    entries = await use_case.execute(experiment_id=experiment_id)
    return [JournalEntryResponse.from_domain(entry) for entry in entries]


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    use_case: Annotated[GetDashboardSnapshotUseCase, Depends(get_dashboard_snapshot_use_case)],
) -> DashboardResponse:
    snapshot: DashboardSnapshot = await use_case.execute()
    return DashboardResponse(
        running=[_experiment_response_from_snapshot(s) for s in snapshot.running],
        needs_decision=[_experiment_response_from_snapshot(s) for s in snapshot.needs_decision],
        recent_journal_entries=[JournalEntryResponse.from_domain(e) for e in snapshot.recent_journal_entries],
    )
