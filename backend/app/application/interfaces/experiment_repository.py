from datetime import datetime
from typing import Protocol

from app.domain.entities.experiment import Experiment, ExperimentStatus, Hypothesis


class ExperimentRepository(Protocol):
    async def create(
        self,
        title: str,
        hypothesis: Hypothesis,
        evaluation_window_days: int,
        created_by_user_id: int | None,
    ) -> Experiment: ...

    async def get_by_id(self, experiment_id: int) -> Experiment | None: ...

    async def list_all(self, status: ExperimentStatus | None = None) -> list[Experiment]: ...

    async def update(
        self,
        experiment_id: int,
        title: str,
        hypothesis: Hypothesis,
        evaluation_window_days: int,
    ) -> Experiment: ...

    async def update_status(
        self,
        experiment_id: int,
        status: ExperimentStatus,
        started_at: datetime | None = None,
        ended_at: datetime | None = None,
    ) -> Experiment: ...
