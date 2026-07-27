"use client";

import { useEffect, useState } from "react";

import { JournalEntryForm, JournalEntryList } from "@/components/admin/journal";
import { listJournalEntries } from "@/lib/admin-api";
import type { JournalEntry } from "@/lib/admin-types";

export function JournalView() {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listJournalEntries()
      .then(setEntries)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <div className="flex max-w-2xl flex-col gap-6">
      <h1 className="text-xl font-semibold">Journal</h1>
      <JournalEntryForm experimentId={null} onAdded={(entry) => setEntries([entry, ...entries])} />
      {error ? <p className="text-sm text-destructive">{error}</p> : <JournalEntryList entries={entries} />}
    </div>
  );
}
