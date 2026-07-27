from dataclasses import dataclass

from app.application.interfaces.evaluation_run_repository import EvaluationRunRepository
from app.application.interfaces.experiment_repository import ExperimentRepository
from app.application.interfaces.journal_entry_repository import JournalEntryRepository
from app.application.interfaces.metric_repository import MetricRepository
from app.domain.entities.evaluation_run import EvaluationRun
from app.domain.entities.experiment import Experiment, ExperimentStatus
from app.domain.entities.journal_entry import JournalEntry
from app.domain.entities.metric import Metric


@dataclass(frozen=True)
class MetricSnapshot:
    metric: Metric
    latest_run: EvaluationRun | None


@dataclass(frozen=True)
class ExperimentSnapshot:
    experiment: Experiment
    metrics: list[MetricSnapshot]


@dataclass(frozen=True)
class DashboardSnapshot:
    running: list[ExperimentSnapshot]
    needs_decision: list[ExperimentSnapshot]
    recent_journal_entries: list[JournalEntry]


class GetDashboardSnapshotUseCase:
    """One aggregate read for Mission Control's home screen — avoids the
    frontend making N round trips to assemble the same view.
    """

    def __init__(
        self,
        experiment_repository: ExperimentRepository,
        metric_repository: MetricRepository,
        evaluation_run_repository: EvaluationRunRepository,
        journal_entry_repository: JournalEntryRepository,
    ) -> None:
        self._experiment_repository = experiment_repository
        self._metric_repository = metric_repository
        self._evaluation_run_repository = evaluation_run_repository
        self._journal_entry_repository = journal_entry_repository

    async def execute(self) -> DashboardSnapshot:
        running_experiments = await self._experiment_repository.list_all(ExperimentStatus.RUNNING)
        evaluating_experiments = await self._experiment_repository.list_all(ExperimentStatus.EVALUATING)

        running = [await self._build_snapshot(experiment) for experiment in running_experiments]
        needs_decision = [await self._build_snapshot(experiment) for experiment in evaluating_experiments]
        recent_journal_entries = await self._journal_entry_repository.list_all(limit=5)

        return DashboardSnapshot(
            running=running,
            needs_decision=needs_decision,
            recent_journal_entries=recent_journal_entries,
        )

    async def _build_snapshot(self, experiment: Experiment) -> ExperimentSnapshot:
        metrics = await self._metric_repository.list_by_experiment(experiment.id)
        metric_snapshots = [
            MetricSnapshot(
                metric=metric,
                latest_run=await self._evaluation_run_repository.get_latest_for_metric(metric.id),
            )
            for metric in metrics
        ]
        return ExperimentSnapshot(experiment=experiment, metrics=metric_snapshots)
