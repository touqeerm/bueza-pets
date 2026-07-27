"use client";

import { useEffect, useState } from "react";

import { AddMetricForm } from "@/components/admin/add-metric-form";
import { JournalEntryForm, JournalEntryList } from "@/components/admin/journal";
import { MetricCard } from "@/components/admin/metric-card";
import { ExperimentStatusBadge } from "@/components/admin/status-badge";
import { Button } from "@/components/ui/button";
import {
  archiveExperiment,
  evaluateExperiment,
  getExperiment,
  listJournalEntries,
  startExperiment,
} from "@/lib/admin-api";
import type { Experiment, JournalEntry } from "@/lib/admin-types";

export function ExperimentDetailView({ experimentId }: { experimentId: number }) {
  const [experiment, setExperiment] = useState<Experiment | null>(null);
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isActing, setIsActing] = useState(false);

  useEffect(() => {
    Promise.all([getExperiment(experimentId), listJournalEntries(experimentId)])
      .then(([experimentData, entriesData]) => {
        setExperiment(experimentData);
        setEntries(entriesData);
      })
      .catch((err: Error) => setError(err.message));
  }, [experimentId]);

  async function runAction(action: () => Promise<Experiment>) {
    setIsActing(true);
    setError(null);
    try {
      setExperiment(await action());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Action failed");
    } finally {
      setIsActing(false);
    }
  }

  if (error && !experiment) return <p className="text-sm text-destructive">{error}</p>;
  if (!experiment) return <p className="text-sm text-muted-foreground">Loading…</p>;

  const isDraft = experiment.status === "draft";
  const canEvaluate = experiment.status === "running" || experiment.status === "evaluating";
  const isTerminal = experiment.status === "archived";

  return (
    <div className="flex max-w-2xl flex-col gap-6">
      <div className="flex items-center justify-between gap-2">
        <h1 className="text-xl font-semibold">{experiment.title}</h1>
        <ExperimentStatusBadge status={experiment.status} />
      </div>

      <section className="rounded-lg border border-border p-4">
        <p className="text-sm font-medium">Hypothesis</p>
        <p className="mt-1 text-sm text-muted-foreground">
          We believe {experiment.hypothesis.action} for {experiment.hypothesis.persona} will result in{" "}
          {experiment.hypothesis.outcome}. We&apos;ll know when {experiment.hypothesis.signal}.
        </p>
      </section>

      <section className="flex flex-col gap-3">
        <p className="text-sm font-semibold text-muted-foreground">METRICS</p>
        {experiment.metrics.length === 0 ? (
          <p className="text-sm text-muted-foreground">No metrics yet.</p>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {experiment.metrics.map((metric) => (
              <MetricCard key={metric.id} metric={metric} />
            ))}
          </div>
        )}
        {isDraft ? (
          <AddMetricForm
            experimentId={experiment.id}
            onAdded={(metric) => setExperiment({ ...experiment, metrics: [...experiment.metrics, metric] })}
          />
        ) : null}
      </section>

      {error ? (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      ) : null}

      <section className="flex gap-2">
        {isDraft ? (
          <Button
            disabled={isActing || experiment.metrics.length === 0}
            onClick={() => runAction(() => startExperiment(experiment.id))}
          >
            Start experiment
          </Button>
        ) : null}
        {canEvaluate ? (
          <Button
            variant="outline"
            disabled={isActing}
            onClick={() => runAction(() => evaluateExperiment(experiment.id))}
          >
            Evaluate now
          </Button>
        ) : null}
        {!isTerminal ? (
          <Button
            variant="ghost"
            disabled={isActing}
            onClick={() => runAction(() => archiveExperiment(experiment.id))}
          >
            Archive
          </Button>
        ) : null}
      </section>

      <section className="flex flex-col gap-3">
        <p className="text-sm font-semibold text-muted-foreground">JOURNAL FOR THIS EXPERIMENT</p>
        <JournalEntryForm experimentId={experiment.id} onAdded={(entry) => setEntries([entry, ...entries])} />
        <JournalEntryList entries={entries} />
      </section>
    </div>
  );
}
