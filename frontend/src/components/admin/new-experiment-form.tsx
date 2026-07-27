"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { createExperiment } from "@/lib/admin-api";

const inputClassName =
  "h-10 w-full rounded-lg border border-border bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50";

export function NewExperimentForm() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [action, setAction] = useState("");
  const [persona, setPersona] = useState("");
  const [outcome, setOutcome] = useState("");
  const [signal, setSignal] = useState("");
  const [evaluationWindowDays, setEvaluationWindowDays] = useState(14);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const experiment = await createExperiment({
        title,
        hypothesis: { action, persona, outcome, signal },
        evaluation_window_days: evaluationWindowDays,
      });
      router.push(`/admin/experiments/${experiment.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create experiment");
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex max-w-xl flex-col gap-4">
      <div className="flex flex-col gap-1">
        <label htmlFor="title" className="text-sm font-medium">
          Title
        </label>
        <input id="title" required value={title} onChange={(e) => setTitle(e.target.value)} className={inputClassName} />
      </div>

      <div className="flex flex-col gap-2 rounded-lg border border-border p-4">
        <p className="text-sm font-medium">Hypothesis</p>
        <label className="text-xs text-muted-foreground">We believe</label>
        <input
          required
          value={action}
          onChange={(e) => setAction(e.target.value)}
          placeholder="doing X"
          className={inputClassName}
        />
        <label className="text-xs text-muted-foreground">for</label>
        <input
          required
          value={persona}
          onChange={(e) => setPersona(e.target.value)}
          placeholder="this persona"
          className={inputClassName}
        />
        <label className="text-xs text-muted-foreground">will result in</label>
        <input
          required
          value={outcome}
          onChange={(e) => setOutcome(e.target.value)}
          placeholder="this outcome"
          className={inputClassName}
        />
        <label className="text-xs text-muted-foreground">We&apos;ll know when</label>
        <input
          required
          value={signal}
          onChange={(e) => setSignal(e.target.value)}
          placeholder="this signal"
          className={inputClassName}
        />
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="window" className="text-sm font-medium">
          Evaluation window (days)
        </label>
        <input
          id="window"
          type="number"
          min={1}
          max={90}
          required
          value={evaluationWindowDays}
          onChange={(e) => setEvaluationWindowDays(Number(e.target.value))}
          className={`${inputClassName} max-w-32`}
        />
      </div>

      {error ? (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      ) : null}

      <Button type="submit" disabled={isSubmitting} className="self-start">
        {isSubmitting ? "Creating…" : "Create draft"}
      </Button>
      <p className="text-xs text-muted-foreground">
        You&apos;ll add metrics and start the experiment from its detail page next.
      </p>
    </form>
  );
}
