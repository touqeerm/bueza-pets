from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class OtpCodeModel(Base):
    __tablename__ = "otp_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(32), index=True)
    code: Mapped[str] = mapped_column(String(6))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class EventModel(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), index=True)
    properties: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    anonymous_id: Mapped[str] = mapped_column(String(64), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)


# ---- Experimentation platform (Tier 1) ----
#
# Status/kind/type fields are stored as plain strings (validated against the
# domain StrEnums in the application layer) rather than native Postgres ENUM
# types — there's no Alembic in this project (schema comes from
# Base.metadata.create_all()), and a native enum requires an ALTER TYPE
# migration to add a new value later. A String column with app-layer
# validation costs nothing extra today and avoids that friction, matching how
# EventModel.name already stores EventName values.


class ExperimentModel(Base):
    __tablename__ = "experiments"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="draft", server_default="draft", index=True)

    hypothesis_action: Mapped[str] = mapped_column(String)
    hypothesis_persona: Mapped[str] = mapped_column(String)
    hypothesis_outcome: Mapped[str] = mapped_column(String)
    hypothesis_signal: Mapped[str] = mapped_column(String)

    evaluation_window_days: Mapped[int] = mapped_column(SmallInteger, default=14, server_default="14")
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    metrics: Mapped[list["MetricModel"]] = relationship(back_populates="experiment", cascade="all, delete-orphan")


class MetricModel(Base):
    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(primary_key=True)
    experiment_id: Mapped[int] = mapped_column(ForeignKey("experiments.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    kind: Mapped[str] = mapped_column(String(20))
    is_guardrail: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    target_value: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    minimum_sample_size: Mapped[int] = mapped_column(Integer, default=100, server_default="100")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    experiment: Mapped[ExperimentModel] = relationship(back_populates="metrics")
    event_mappings: Mapped[list["EventMappingModel"]] = relationship(
        back_populates="metric", cascade="all, delete-orphan"
    )


class EventMappingModel(Base):
    __tablename__ = "event_mappings"

    id: Mapped[int] = mapped_column(primary_key=True)
    metric_id: Mapped[int] = mapped_column(ForeignKey("metrics.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    event_name: Mapped[str] = mapped_column(String(64))
    property_filters: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)

    metric: Mapped[MetricModel] = relationship(back_populates="event_mappings")


class EvaluationRunModel(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    metric_id: Mapped[int] = mapped_column(ForeignKey("metrics.id", ondelete="CASCADE"), index=True)
    ran_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    sample_size: Mapped[int] = mapped_column(Integer)
    current_value: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    status: Mapped[str] = mapped_column(String(20))
    recommendation: Mapped[str] = mapped_column(String)


class JournalEntryModel(Base):
    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    experiment_id: Mapped[int | None] = mapped_column(
        ForeignKey("experiments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    entry_type: Mapped[str] = mapped_column(String(30), index=True)
    body: Mapped[str] = mapped_column(String)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
