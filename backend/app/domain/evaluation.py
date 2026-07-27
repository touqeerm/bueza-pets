"""Pure evaluation logic for the experimentation engine.

Deliberately single-arm (a metric clears a target threshold, not a
control-vs-variant comparison) — early-stage traffic volumes rarely support a
trustworthy two-arm significance test, and Lean Startup's own "validated
learning" framing is about whether a signal is strong enough to act on, not
about beating a control group. A Wilson score interval (rather than a raw
point estimate) is what makes "60% on 12 samples" read differently from "60%
on 400 samples" without needing a second arm to compare against.
"""

import math
from dataclasses import dataclass
from decimal import Decimal

from app.domain.entities.metric import MetricKind, MetricStatus

DEFAULT_CONFIDENCE = 0.90
_Z_SCORES = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}


@dataclass(frozen=True)
class EvaluationOutcome:
    current_value: Decimal
    sample_size: int
    status: MetricStatus
    recommendation: str


def _round(value: float) -> Decimal:
    return Decimal(str(round(value, 4)))


def _wilson_interval(successes: int, n: int, confidence: float) -> tuple[Decimal, Decimal]:
    z = _Z_SCORES[confidence]
    phat = successes / n
    denominator = 1 + z**2 / n
    center = phat + z**2 / (2 * n)
    margin = z * math.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))
    lower = max(0.0, (center - margin) / denominator)
    upper = min(1.0, (center + margin) / denominator)
    return _round(lower), _round(upper)


def evaluate_metric(
    *,
    kind: MetricKind,
    numerator: int,
    denominator: int,
    minimum_sample_size: int,
    target_value: Decimal,
    is_guardrail: bool,
    confidence: float = DEFAULT_CONFIDENCE,
) -> EvaluationOutcome:
    sample_size = denominator if kind in (MetricKind.CONVERSION_RATE, MetricKind.RATIO) else numerator

    if sample_size < minimum_sample_size:
        current_value = _round(numerator / denominator) if denominator else Decimal("0")
        return EvaluationOutcome(
            current_value=current_value,
            sample_size=sample_size,
            status=MetricStatus.INSUFFICIENT_DATA,
            recommendation=f"Only {sample_size} of {minimum_sample_size} required samples collected — keep running.",
        )

    if kind is MetricKind.COUNT:
        current_value = Decimal(numerator)
        met = current_value >= target_value
        status = MetricStatus.MET_TARGET if met else MetricStatus.ON_TRACK
        recommendation = (
            f"Reached {numerator} against a target of {target_value}."
            if met
            else f"At {numerator} against a target of {target_value} — let it keep running."
        )
        return EvaluationOutcome(current_value, sample_size, status, recommendation)

    current_value = _round(numerator / denominator) if denominator else Decimal("0")
    lower, upper = _wilson_interval(numerator, denominator, confidence)
    confidence_pct = int(confidence * 100)

    if is_guardrail:
        if upper < target_value:
            return EvaluationOutcome(
                current_value,
                sample_size,
                MetricStatus.AT_RISK,
                f"Guardrail breached with {confidence_pct}% confidence (n={sample_size}): "
                f"{current_value} is below the {target_value} floor.",
            )
        if lower >= target_value:
            return EvaluationOutcome(
                current_value,
                sample_size,
                MetricStatus.MET_TARGET,
                f"Guardrail holding at {current_value} (n={sample_size}).",
            )
        return EvaluationOutcome(
            current_value,
            sample_size,
            MetricStatus.ON_TRACK,
            f"Guardrail trending fine at {current_value}, but n={sample_size} isn't conclusive yet.",
        )

    if lower >= target_value:
        status = MetricStatus.MET_TARGET
        recommendation = (
            f"Target met with {confidence_pct}% confidence (n={sample_size}): {current_value} vs target "
            f"{target_value}. Consider marking this experiment validated."
        )
    elif upper < target_value:
        status = MetricStatus.MISSED_TARGET
        recommendation = (
            f"Missed target with {confidence_pct}% confidence (n={sample_size}): {current_value} vs target "
            f"{target_value}. Consider invalidating and logging why."
        )
    else:
        status = MetricStatus.ON_TRACK
        recommendation = f"Trending at {current_value} (n={sample_size}) but not yet conclusive vs target {target_value}."

    return EvaluationOutcome(current_value, sample_size, status, recommendation)
