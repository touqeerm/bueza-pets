from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.domain.entities.evaluation_run import EvaluationRun
from app.domain.entities.experiment import Experiment, ExperimentStatus
from app.domain.entities.journal_entry import JournalEntry, JournalEntryType
from app.domain.entities.metric import EventMapping, EventMappingRole, Metric, MetricKind, MetricStatus
from app.domain.events import EventName


class HypothesisSchema(BaseModel):
    action: str = Field(min_length=1)
    persona: str = Field(min_length=1)
    outcome: str = Field(min_length=1)
    signal: str = Field(min_length=1)


class ExperimentCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    hypothesis: HypothesisSchema
    evaluation_window_days: int = Field(default=14, ge=1, le=90)


class ExperimentUpdateRequest(ExperimentCreateRequest):
    pass


class EventMappingSchema(BaseModel):
    role: EventMappingRole
    event_name: EventName
    property_filters: dict[str, Any] = Field(default_factory=dict)


class MetricCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    kind: MetricKind
    is_guardrail: bool = False
    target_value: Decimal
    minimum_sample_size: int = Field(default=100, ge=1)
    event_mappings: list[EventMappingSchema] = Field(min_length=1)


class EventMappingResponse(BaseModel):
    id: int
    role: str
    event_name: str
    property_filters: dict[str, Any]

    @classmethod
    def from_domain(cls, mapping: EventMapping) -> "EventMappingResponse":
        return cls(
            id=mapping.id,
            role=mapping.role,
            event_name=mapping.event_name,
            property_filters=mapping.property_filters,
        )


class EvaluationRunResponse(BaseModel):
    id: int
    ran_at: datetime
    sample_size: int
    current_value: Decimal
    status: MetricStatus
    recommendation: str

    @classmethod
    def from_domain(cls, run: EvaluationRun) -> "EvaluationRunResponse":
        return cls(
            id=run.id,
            ran_at=run.ran_at,
            sample_size=run.sample_size,
            current_value=run.current_value,
            status=run.status,
            recommendation=run.recommendation,
        )


class MetricResponse(BaseModel):
    id: int
    name: str
    kind: MetricKind
    is_guardrail: bool
    target_value: Decimal
    minimum_sample_size: int
    event_mappings: list[EventMappingResponse]
    latest_run: EvaluationRunResponse | None = None

    @classmethod
    def from_domain(cls, metric: Metric, latest_run: EvaluationRun | None = None) -> "MetricResponse":
        return cls(
            id=metric.id,
            name=metric.name,
            kind=metric.kind,
            is_guardrail=metric.is_guardrail,
            target_value=metric.target_value,
            minimum_sample_size=metric.minimum_sample_size,
            event_mappings=[EventMappingResponse.from_domain(mapping) for mapping in metric.event_mappings],
            latest_run=EvaluationRunResponse.from_domain(latest_run) if latest_run else None,
        )


class ExperimentResponse(BaseModel):
    id: int
    title: str
    status: ExperimentStatus
    hypothesis: HypothesisSchema
    evaluation_window_days: int
    started_at: datetime | None
    ended_at: datetime | None
    created_at: datetime
    metrics: list[MetricResponse] = Field(default_factory=list)

    @classmethod
    def from_domain(cls, experiment: Experiment, metrics: list[MetricResponse] | None = None) -> "ExperimentResponse":
        return cls(
            id=experiment.id,
            title=experiment.title,
            status=experiment.status,
            hypothesis=HypothesisSchema(
                action=experiment.hypothesis.action,
                persona=experiment.hypothesis.persona,
                outcome=experiment.hypothesis.outcome,
                signal=experiment.hypothesis.signal,
            ),
            evaluation_window_days=experiment.evaluation_window_days,
            started_at=experiment.started_at,
            ended_at=experiment.ended_at,
            created_at=experiment.created_at,
            metrics=metrics or [],
        )


class JournalEntryCreateRequest(BaseModel):
    entry_type: JournalEntryType
    body: str = Field(min_length=1)
    experiment_id: int | None = None


class JournalEntryResponse(BaseModel):
    id: int
    experiment_id: int | None
    entry_type: JournalEntryType
    body: str
    created_at: datetime

    @classmethod
    def from_domain(cls, entry: JournalEntry) -> "JournalEntryResponse":
        return cls(
            id=entry.id,
            experiment_id=entry.experiment_id,
            entry_type=entry.entry_type,
            body=entry.body,
            created_at=entry.created_at,
        )


class DashboardResponse(BaseModel):
    running: list[ExperimentResponse]
    needs_decision: list[ExperimentResponse]
    recent_journal_entries: list[JournalEntryResponse]
