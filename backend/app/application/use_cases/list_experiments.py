from app.application.interfaces.experiment_repository import ExperimentRepository
from app.domain.entities.experiment import Experiment, ExperimentStatus


class ListExperimentsUseCase:
    def __init__(self, experiment_repository: ExperimentRepository) -> None:
        self._experiment_repository = experiment_repository

    async def execute(self, status: ExperimentStatus | None = None) -> list[Experiment]:
        return await self._experiment_repository.list_all(status)
