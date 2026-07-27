from app.application.interfaces.evaluation_run_repository import EvaluationRunRepository
from app.application.interfaces.experiment_repository import ExperimentRepository
from app.application.interfaces.metric_repository import MetricRepository
from app.application.use_cases.get_dashboard_snapshot import ExperimentSnapshot, MetricSnapshot


class GetExperimentDetailUseCase:
    def __init__(
        self,
        experiment_repository: ExperimentRepository,
        metric_repository: MetricRepository,
        evaluation_run_repository: EvaluationRunRepository,
    ) -> None:
        self._experiment_repository = experiment_repository
        self._metric_repository = metric_repository
        self._evaluation_run_repository = evaluation_run_repository

    async def execute(self, experiment_id: int) -> ExperimentSnapshot | None:
        experiment = await self._experiment_repository.get_by_id(experiment_id)
        if experiment is None:
            return None

        metrics = await self._metric_repository.list_by_experiment(experiment_id)
        metric_snapshots = [
            MetricSnapshot(
                metric=metric,
                latest_run=await self._evaluation_run_repository.get_latest_for_metric(metric.id),
            )
            for metric in metrics
        ]
        return ExperimentSnapshot(experiment=experiment, metrics=metric_snapshots)
