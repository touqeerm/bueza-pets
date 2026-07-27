from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.experiment import Experiment, ExperimentStatus, Hypothesis
from app.infrastructure.database.models import ExperimentModel


class SqlAlchemyExperimentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        title: str,
        hypothesis: Hypothesis,
        evaluation_window_days: int,
        created_by_user_id: int | None,
    ) -> Experiment:
        model = ExperimentModel(
            title=title,
            hypothesis_action=hypothesis.action,
            hypothesis_persona=hypothesis.persona,
            hypothesis_outcome=hypothesis.outcome,
            hypothesis_signal=hypothesis.signal,
            evaluation_window_days=evaluation_window_days,
            created_by_user_id=created_by_user_id,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, experiment_id: int) -> Experiment | None:
        model = await self._session.get(ExperimentModel, experiment_id)
        return self._to_entity(model) if model else None

    async def list_all(self, status: ExperimentStatus | None = None) -> list[Experiment]:
        query = select(ExperimentModel).order_by(ExperimentModel.created_at.desc())
        if status is not None:
            query = query.where(ExperimentModel.status == status.value)
        result = await self._session.execute(query)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def update(
        self,
        experiment_id: int,
        title: str,
        hypothesis: Hypothesis,
        evaluation_window_days: int,
    ) -> Experiment:
        model = await self._session.get(ExperimentModel, experiment_id)
        model.title = title
        model.hypothesis_action = hypothesis.action
        model.hypothesis_persona = hypothesis.persona
        model.hypothesis_outcome = hypothesis.outcome
        model.hypothesis_signal = hypothesis.signal
        model.evaluation_window_days = evaluation_window_days
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def update_status(
        self,
        experiment_id: int,
        status: ExperimentStatus,
        started_at: datetime | None = None,
        ended_at: datetime | None = None,
    ) -> Experiment:
        model = await self._session.get(ExperimentModel, experiment_id)
        model.status = status.value
        if started_at is not None:
            model.started_at = started_at
        if ended_at is not None:
            model.ended_at = ended_at
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: ExperimentModel) -> Experiment:
        return Experiment(
            id=model.id,
            title=model.title,
            status=ExperimentStatus(model.status),
            hypothesis=Hypothesis(
                action=model.hypothesis_action,
                persona=model.hypothesis_persona,
                outcome=model.hypothesis_outcome,
                signal=model.hypothesis_signal,
            ),
            evaluation_window_days=model.evaluation_window_days,
            started_at=model.started_at,
            ended_at=model.ended_at,
            created_by_user_id=model.created_by_user_id,
            created_at=model.created_at,
        )
