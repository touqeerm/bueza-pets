from app.application.interfaces.experiment_repository import ExperimentRepository
from app.domain.entities.experiment import Experiment, Hypothesis


class CreateExperimentUseCase:
    def __init__(self, experiment_repository: ExperimentRepository) -> None:
        self._experiment_repository = experiment_repository

    async def execute(
        self,
        title: str,
        hypothesis: Hypothesis,
        evaluation_window_days: int,
        created_by_user_id: int | None,
    ) -> Experiment:
        return await self._experiment_repository.create(
            title=title,
            hypothesis=hypothesis,
            evaluation_window_days=evaluation_window_days,
            created_by_user_id=created_by_user_id,
        )
