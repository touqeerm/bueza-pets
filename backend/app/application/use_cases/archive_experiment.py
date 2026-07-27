from app.application.interfaces.experiment_repository import ExperimentRepository
from app.domain.entities.experiment import Experiment, ExperimentStatus


class ArchiveExperimentUseCase:
    def __init__(self, experiment_repository: ExperimentRepository) -> None:
        self._experiment_repository = experiment_repository

    async def execute(self, experiment_id: int) -> Experiment:
        return await self._experiment_repository.update_status(experiment_id, ExperimentStatus.ARCHIVED)
