from decimal import Decimal
from typing import Any, Protocol

from app.domain.entities.metric import EventMappingRole, Metric, MetricKind


class MetricRepository(Protocol):
    async def create(
        self,
        experiment_id: int,
        name: str,
        kind: MetricKind,
        is_guardrail: bool,
        target_value: Decimal,
        minimum_sample_size: int,
        event_mappings: list[tuple[EventMappingRole, str, dict[str, Any]]],
    ) -> Metric: ...

    async def get_by_id(self, metric_id: int) -> Metric | None: ...

    async def list_by_experiment(self, experiment_id: int) -> list[Metric]: ...

    async def delete(self, metric_id: int) -> None: ...
