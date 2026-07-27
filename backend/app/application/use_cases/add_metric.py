from decimal import Decimal
from typing import Any

from app.application.interfaces.experiment_repository import ExperimentRepository
from app.application.interfaces.metric_repository import MetricRepository
from app.domain.entities.experiment import ExperimentStatus
from app.domain.entities.metric import EventMappingRole, Metric, MetricKind
from app.domain.errors import InvalidExperimentTransitionError


class AddMetricUseCase:
    def __init__(self, experiment_repository: ExperimentRepository, metric_repository: MetricRepository) -> None:
        self._experiment_repository = experiment_repository
        self._metric_repository = metric_repository

    async def execute(
        self,
        experiment_id: int,
        name: str,
        kind: MetricKind,
        is_guardrail: bool,
        target_value: Decimal,
        minimum_sample_size: int,
        event_mappings: list[tuple[EventMappingRole, str, dict[str, Any]]],
    ) -> Metric:
        experiment = await self._experiment_repository.get_by_id(experiment_id)
        if experiment is None or experiment.status is not ExperimentStatus.DRAFT:
            raise InvalidExperimentTransitionError("Metrics can only be added while an experiment is in draft")

        return await self._metric_repository.create(
            experiment_id=experiment_id,
            name=name,
            kind=kind,
            is_guardrail=is_guardrail,
            target_value=target_value,
            minimum_sample_size=minimum_sample_size,
            event_mappings=event_mappings,
        )
