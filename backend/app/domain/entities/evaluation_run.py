from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.domain.entities.metric import MetricStatus


@dataclass(frozen=True)
class EvaluationRun:
    id: int
    metric_id: int
    ran_at: datetime
    sample_size: int
    current_value: Decimal
    status: MetricStatus
    recommendation: str
