from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.evaluation_run import EvaluationRun
from app.domain.entities.metric import MetricStatus
from app.infrastructure.database.models import EvaluationRunModel


class SqlAlchemyEvaluationRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        metric_id: int,
        sample_size: int,
        current_value: Decimal,
        status: MetricStatus,
        recommendation: str,
    ) -> EvaluationRun:
        model = EvaluationRunModel(
            metric_id=metric_id,
            sample_size=sample_size,
            current_value=current_value,
            status=status.value,
            recommendation=recommendation,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_latest_for_metric(self, metric_id: int) -> EvaluationRun | None:
        result = await self._session.execute(
            select(EvaluationRunModel)
            .where(EvaluationRunModel.metric_id == metric_id)
            .order_by(EvaluationRunModel.ran_at.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_for_metric(self, metric_id: int) -> list[EvaluationRun]:
        result = await self._session.execute(
            select(EvaluationRunModel)
            .where(EvaluationRunModel.metric_id == metric_id)
            .order_by(EvaluationRunModel.ran_at)
        )
        return [self._to_entity(model) for model in result.scalars().all()]

    @staticmethod
    def _to_entity(model: EvaluationRunModel) -> EvaluationRun:
        return EvaluationRun(
            id=model.id,
            metric_id=model.metric_id,
            ran_at=model.ran_at,
            sample_size=model.sample_size,
            current_value=model.current_value,
            status=MetricStatus(model.status),
            recommendation=model.recommendation,
        )
