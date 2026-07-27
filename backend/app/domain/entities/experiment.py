from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class ExperimentStatus(StrEnum):
    DRAFT = "draft"
    RUNNING = "running"
    EVALUATING = "evaluating"
    VALIDATED = "validated"
    INVALIDATED = "invalidated"
    INCONCLUSIVE = "inconclusive"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class Hypothesis:
    action: str
    persona: str
    outcome: str
    signal: str


@dataclass(frozen=True)
class Experiment:
    id: int
    title: str
    status: ExperimentStatus
    hypothesis: Hypothesis
    evaluation_window_days: int
    started_at: datetime | None
    ended_at: datetime | None
    created_by_user_id: int | None
    created_at: datetime
