from app.application.interfaces.experiment_repository import ExperimentRepository
from app.application.interfaces.metric_repository import MetricRepository
from app.domain.entities.experiment import ExperimentStatus
from app.domain.errors import InvalidExperimentTransitionError


class RemoveMetricUseCase:
    def __init__(self, experiment_repository: ExperimentRepository, metric_repository: MetricRepository) -> None:
        self._experiment_repository = experiment_repository
        self._metric_repository = metric_repository

    async def execute(self, experiment_id: int, metric_id: int) -> None:
        experiment = await self._experiment_repository.get_by_id(experiment_id)
        if experiment is None or experiment.status is not ExperimentStatus.DRAFT:
            raise InvalidExperimentTransitionError("Metrics can only be removed while an experiment is in draft")

        await self._metric_repository.delete(metric_id)
