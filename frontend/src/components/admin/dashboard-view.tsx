"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { ExperimentCard } from "@/components/admin/experiment-card";
import { JournalEntryList } from "@/components/admin/journal";
import { Button } from "@/components/ui/button";
import { getDashboard } from "@/lib/admin-api";
import type { DashboardSnapshot } from "@/lib/admin-types";

export function DashboardView() {
  const [snapshot, setSnapshot] = useState<DashboardSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDashboard()
      .then(setSnapshot)
      .catch((err: Error) => setError(err.message));
  }, []);

  if (error) return <p className="text-sm text-destructive">{error}</p>;
  if (!snapshot) return <p className="text-sm text-muted-foreground">Loading…</p>;

  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold">Mission Control</h1>
        <Link href="/admin/experiments/new">
          <Button size="sm">+ New experiment</Button>
        </Link>
      </div>

      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-muted-foreground">RUNNING ({snapshot.running.length})</h2>
        {snapshot.running.length === 0 ? (
          <p className="text-sm text-muted-foreground">No experiments running right now.</p>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {snapshot.running.map((experiment) => (
              <ExperimentCard key={experiment.id} experiment={experiment} />
            ))}
          </div>
        )}
      </section>

      <section className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold text-muted-foreground">
          NEEDS DECISION ({snapshot.needs_decision.length})
        </h2>
        {snapshot.needs_decision.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nothing awaiting a call right now.</p>
        ) : (
          <div className="grid gap-3 sm:grid-cols-2">
            {snapshot.needs_decision.map((experiment) => (
              <ExperimentCard key={experiment.id} experiment={experiment} />
            ))}
          </div>
        )}
      </section>

      <section className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-muted-foreground">RECENT JOURNAL</h2>
          <Link href="/admin/journal" className="text-sm text-primary hover:underline">
            View all →
          </Link>
        </div>
        <JournalEntryList entries={snapshot.recent_journal_entries} />
      </section>
    </div>
  );
}
