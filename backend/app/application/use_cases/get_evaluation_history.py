from app.application.interfaces.evaluation_run_repository import EvaluationRunRepository
from app.domain.entities.evaluation_run import EvaluationRun


class GetEvaluationHistoryUseCase:
    def __init__(self, evaluation_run_repository: EvaluationRunRepository) -> None:
        self._evaluation_run_repository = evaluation_run_repository

    async def execute(self, metric_id: int) -> list[EvaluationRun]:
        return await self._evaluation_run_repository.list_for_metric(metric_id)
