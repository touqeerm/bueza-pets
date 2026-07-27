from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.metric import EventMapping, EventMappingRole, Metric, MetricKind
from app.infrastructure.database.models import EventMappingModel, MetricModel


class SqlAlchemyMetricRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        experiment_id: int,
        name: str,
        kind: MetricKind,
        is_guardrail: bool,
        target_value: Decimal,
        minimum_sample_size: int,
        event_mappings: list[tuple[EventMappingRole, str, dict[str, Any]]],
    ) -> Metric:
        model = MetricModel(
            experiment_id=experiment_id,
            name=name,
            kind=kind.value,
            is_guardrail=is_guardrail,
            target_value=target_value,
            minimum_sample_size=minimum_sample_size,
            event_mappings=[
                EventMappingModel(role=role, event_name=event_name, property_filters=property_filters)
                for role, event_name, property_filters in event_mappings
            ],
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model, attribute_names=["event_mappings"])
        return self._to_entity(model)

    async def get_by_id(self, metric_id: int) -> Metric | None:
        result = await self._session.execute(
            select(MetricModel).where(MetricModel.id == metric_id).options(selectinload(MetricModel.event_mappings))
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_experiment(self, experiment_id: int) -> list[Metric]:
        result = await self._session.execute(
            select(MetricModel)
            .where(MetricModel.experiment_id == experiment_id)
            .options(selectinload(MetricModel.event_mappings))
            .order_by(MetricModel.created_at)
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    async def delete(self, metric_id: int) -> None:
        model = await self._session.get(MetricModel, metric_id)
        if model is not None:
            await self._session.delete(model)
            await self._session.commit()

    @staticmethod
    def _to_entity(model: MetricModel) -> Metric:
        return Metric(
            id=model.id,
            experiment_id=model.experiment_id,
            name=model.name,
            kind=MetricKind(model.kind),
            is_guardrail=model.is_guardrail,
            target_value=model.target_value,
            minimum_sample_size=model.minimum_sample_size,
            event_mappings=[
                EventMapping(
                    id=mapping.id,
                    role=mapping.role,
                    event_name=mapping.event_name,
                    property_filters=mapping.property_filters,
                )
                for mapping in model.event_mappings
            ],
        )
