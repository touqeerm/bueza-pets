from datetime import datetime, timezone

from app.application.interfaces.evaluation_run_repository import EvaluationRunRepository
from app.application.interfaces.event_repository import EventRepository
from app.application.interfaces.experiment_repository import ExperimentRepository
from app.application.interfaces.metric_repository import MetricRepository
from app.domain.entities.experiment import Experiment, ExperimentStatus
from app.domain.entities.metric import MetricStatus
from app.domain.errors import ExperimentNotEvaluableError, InvalidExperimentTransitionError
from app.domain.evaluation import evaluate_metric


class EvaluateExperimentUseCase:
    """The Evaluation Engine. Reads live from the existing `events` table via
    each metric's event mappings — nothing about events is duplicated here.
    """

    def __init__(
        self,
        experiment_repository: ExperimentRepository,
        metric_repository: MetricRepository,
        event_repository: EventRepository,
        evaluation_run_repository: EvaluationRunRepository,
    ) -> None:
        self._experiment_repository = experiment_repository
        self._metric_repository = metric_repository
        self._event_repository = event_repository
        self._evaluation_run_repository = evaluation_run_repository

    async def execute(self, experiment_id: int) -> Experiment:
        experiment = await self._experiment_repository.get_by_id(experiment_id)
        if experiment is None:
            raise InvalidExperimentTransitionError("Experiment not found")
        if experiment.status not in (ExperimentStatus.RUNNING, ExperimentStatus.EVALUATING):
            return experiment

        metrics = await self._metric_repository.list_by_experiment(experiment_id)
        if not metrics:
            raise ExperimentNotEvaluableError("An experiment needs at least one metric to be evaluated")

        statuses: list[MetricStatus] = []
        for metric in metrics:
            numerator_mapping = next(m for m in metric.event_mappings if m.role in ("numerator", "count_target"))
            denominator_mapping = next((m for m in metric.event_mappings if m.role == "denominator"), None)

            numerator = await self._event_repository.count_distinct_actors(
                numerator_mapping.event_name, experiment.started_at, numerator_mapping.property_filters
            )
            denominator = (
                await self._event_repository.count_distinct_actors(
                    denominator_mapping.event_name, experiment.started_at, denominator_mapping.property_filters
                )
                if denominator_mapping
                else numerator
            )

            outcome = evaluate_metric(
                kind=metric.kind,
                numerator=numerator,
                denominator=denominator,
                minimum_sample_size=metric.minimum_sample_size,
                target_value=metric.target_value,
                is_guardrail=metric.is_guardrail,
            )
            await self._evaluation_run_repository.create(
                metric_id=metric.id,
                sample_size=outcome.sample_size,
                current_value=outcome.current_value,
                status=outcome.status,
                recommendation=outcome.recommendation,
            )
            statuses.append(outcome.status)

        now = datetime.now(timezone.utc)
        window_elapsed = (now - experiment.started_at).days >= experiment.evaluation_window_days

        if not window_elapsed:
            if experiment.status is ExperimentStatus.RUNNING:
                return await self._experiment_repository.update_status(experiment_id, ExperimentStatus.EVALUATING)
            return experiment

        return await self._experiment_repository.update_status(
            experiment_id, self._determine_final_status(statuses), ended_at=now
        )

    @staticmethod
    def _determine_final_status(statuses: list[MetricStatus]) -> ExperimentStatus:
        if MetricStatus.AT_RISK in statuses or MetricStatus.MISSED_TARGET in statuses:
            return ExperimentStatus.INVALIDATED
        if all(status is MetricStatus.MET_TARGET for status in statuses):
            return ExperimentStatus.VALIDATED
        return ExperimentStatus.INCONCLUSIVE
