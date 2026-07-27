from app.application.interfaces.experiment_repository import ExperimentRepository
from app.domain.entities.experiment import Experiment, ExperimentStatus, Hypothesis
from app.domain.errors import InvalidExperimentTransitionError


class UpdateExperimentUseCase:
    def __init__(self, experiment_repository: ExperimentRepository) -> None:
        self._experiment_repository = experiment_repository

    async def execute(
        self,
        experiment_id: int,
        title: str,
        hypothesis: Hypothesis,
        evaluation_window_days: int,
    ) -> Experiment:
        experiment = await self._experiment_repository.get_by_id(experiment_id)
        if experiment is None or experiment.status is not ExperimentStatus.DRAFT:
            raise InvalidExperimentTransitionError("An experiment can only be edited while in draft")

        return await self._experiment_repository.update(
            experiment_id=experiment_id,
            title=title,
            hypothesis=hypothesis,
            evaluation_window_days=evaluation_window_days,
        )
