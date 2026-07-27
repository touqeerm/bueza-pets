"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { addMetric } from "@/lib/admin-api";
import { METRIC_KINDS, TRACKABLE_EVENTS, type Metric, type MetricKind } from "@/lib/admin-types";

const inputClassName =
  "h-9 w-full rounded-lg border border-border bg-background px-2.5 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50";
const selectClassName = inputClassName;

export function AddMetricForm({ experimentId, onAdded }: { experimentId: number; onAdded: (metric: Metric) => void }) {
  const [name, setName] = useState("");
  const [kind, setKind] = useState<MetricKind>("conversion_rate");
  const [isGuardrail, setIsGuardrail] = useState(false);
  const [targetValue, setTargetValue] = useState("0.60");
  const [minimumSampleSize, setMinimumSampleSize] = useState(100);
  const [numeratorEvent, setNumeratorEvent] = useState<string>(TRACKABLE_EVENTS[0]);
  const [denominatorEvent, setDenominatorEvent] = useState<string>(TRACKABLE_EVENTS[0]);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const needsDenominator = kind !== "count";

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const metric = await addMetric(experimentId, {
        name,
        kind,
        is_guardrail: isGuardrail,
        target_value: Number(targetValue),
        minimum_sample_size: minimumSampleSize,
        event_mappings: needsDenominator
          ? [
              { role: "numerator", event_name: numeratorEvent, property_filters: {} },
              { role: "denominator", event_name: denominatorEvent, property_filters: {} },
            ]
          : [{ role: "count_target", event_name: numeratorEvent, property_filters: {} }],
      });
      onAdded(metric);
      setName("");
      setTargetValue("0.60");
      setMinimumSampleSize(100);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add metric");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2 rounded-lg border border-border p-4">
      <p className="text-sm font-medium">Add metric</p>

      <label className="text-xs text-muted-foreground">Name</label>
      <input required value={name} onChange={(e) => setName(e.target.value)} className={inputClassName} />

      <label className="text-xs text-muted-foreground">Kind</label>
      <select value={kind} onChange={(e) => setKind(e.target.value as MetricKind)} className={selectClassName}>
        {METRIC_KINDS.map((k) => (
          <option key={k} value={k}>
            {k.replace(/_/g, " ")}
          </option>
        ))}
      </select>

      <div className="flex gap-2">
        <div className="flex-1">
          <label className="text-xs text-muted-foreground">Target</label>
          <input
            required
            type="number"
            step="0.0001"
            value={targetValue}
            onChange={(e) => setTargetValue(e.target.value)}
            className={inputClassName}
          />
        </div>
        <div className="flex-1">
          <label className="text-xs text-muted-foreground">Min sample size</label>
          <input
            required
            type="number"
            min={1}
            value={minimumSampleSize}
            onChange={(e) => setMinimumSampleSize(Number(e.target.value))}
            className={inputClassName}
          />
        </div>
      </div>

      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={isGuardrail} onChange={(e) => setIsGuardrail(e.target.checked)} />
        Guardrail (must not regress below target)
      </label>

      <label className="text-xs text-muted-foreground">{needsDenominator ? "Numerator event" : "Count event"}</label>
      <select value={numeratorEvent} onChange={(e) => setNumeratorEvent(e.target.value)} className={selectClassName}>
        {TRACKABLE_EVENTS.map((event) => (
          <option key={event} value={event}>
            {event}
          </option>
        ))}
      </select>

      {needsDenominator ? (
        <>
          <label className="text-xs text-muted-foreground">Denominator event</label>
          <select value={denominatorEvent} onChange={(e) => setDenominatorEvent(e.target.value)} className={selectClassName}>
            {TRACKABLE_EVENTS.map((event) => (
              <option key={event} value={event}>
                {event}
              </option>
            ))}
          </select>
        </>
      ) : null}

      {error ? (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      ) : null}

      <Button type="submit" disabled={isSubmitting} size="sm" className="self-start">
        Add metric
      </Button>
    </form>
  );
}
