from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Any, Literal


class MetricKind(StrEnum):
    CONVERSION_RATE = "conversion_rate"
    COUNT = "count"
    RATIO = "ratio"


class MetricStatus(StrEnum):
    INSUFFICIENT_DATA = "insufficient_data"
    ON_TRACK = "on_track"
    MET_TARGET = "met_target"
    MISSED_TARGET = "missed_target"
    AT_RISK = "at_risk"


EventMappingRole = Literal["numerator", "denominator", "count_target"]


@dataclass(frozen=True)
class EventMapping:
    id: int
    role: EventMappingRole
    event_name: str
    property_filters: dict[str, Any]


@dataclass(frozen=True)
class Metric:
    id: int
    experiment_id: int
    name: str
    kind: MetricKind
    is_guardrail: bool
    target_value: Decimal
    minimum_sample_size: int
    event_mappings: list[EventMapping]
