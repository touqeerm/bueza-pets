from decimal import Decimal
from typing import Protocol

from app.domain.entities.evaluation_run import EvaluationRun
from app.domain.entities.metric import MetricStatus


class EvaluationRunRepository(Protocol):
    async def create(
        self,
        metric_id: int,
        sample_size: int,
        current_value: Decimal,
        status: MetricStatus,
        recommendation: str,
    ) -> EvaluationRun: ...

    async def get_latest_for_metric(self, metric_id: int) -> EvaluationRun | None: ...

    async def list_for_metric(self, metric_id: int) -> list[EvaluationRun]: ...
