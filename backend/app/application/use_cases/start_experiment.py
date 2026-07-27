from datetime import datetime, timezone

from app.application.interfaces.experiment_repository import ExperimentRepository
from app.application.interfaces.metric_repository import MetricRepository
from app.domain.entities.experiment import Experiment, ExperimentStatus
from app.domain.errors import ExperimentNotEvaluableError, InvalidExperimentTransitionError


class StartExperimentUseCase:
    def __init__(self, experiment_repository: ExperimentRepository, metric_repository: MetricRepository) -> None:
        self._experiment_repository = experiment_repository
        self._metric_repository = metric_repository

    async def execute(self, experiment_id: int) -> Experiment:
        experiment = await self._experiment_repository.get_by_id(experiment_id)
        if experiment is None or experiment.status is not ExperimentStatus.DRAFT:
            raise InvalidExperimentTransitionError("Only a draft experiment can be started")

        metrics = await self._metric_repository.list_by_experiment(experiment_id)
        if not metrics:
            raise ExperimentNotEvaluableError("An experiment needs at least one metric before it can start")

        return await self._experiment_repository.update_status(
            experiment_id,
            ExperimentStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )
