"use client";

import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { addJournalEntry } from "@/lib/admin-api";
import { JOURNAL_ENTRY_TYPES, type JournalEntry, type JournalEntryType } from "@/lib/admin-types";

const selectClassName =
  "h-9 w-fit rounded-lg border border-border bg-background px-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50";

export function JournalEntryForm({
  experimentId,
  onAdded,
}: {
  experimentId: number | null;
  onAdded: (entry: JournalEntry) => void;
}) {
  const [entryType, setEntryType] = useState<JournalEntryType>("observation");
  const [body, setBody] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!body.trim()) return;
    setIsSubmitting(true);
    try {
      const entry = await addJournalEntry({ entry_type: entryType, body, experiment_id: experimentId });
      onAdded(entry);
      setBody("");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      <select
        value={entryType}
        onChange={(event) => setEntryType(event.target.value as JournalEntryType)}
        className={selectClassName}
      >
        {JOURNAL_ENTRY_TYPES.map((type) => (
          <option key={type} value={type}>
            {type.replace(/_/g, " ")}
          </option>
        ))}
      </select>
      <Textarea
        value={body}
        onChange={(event) => setBody(event.target.value)}
        placeholder="What did you observe or decide?"
        required
      />
      <Button type="submit" disabled={isSubmitting} size="sm" className="self-start">
        Add entry
      </Button>
    </form>
  );
}

export function JournalEntryList({ entries }: { entries: JournalEntry[] }) {
  if (entries.length === 0) {
    return <p className="text-sm text-muted-foreground">No journal entries yet.</p>;
  }

  return (
    <ul className="flex flex-col gap-2">
      {entries.map((entry) => (
        <li key={entry.id} className="rounded-lg border border-border p-3 text-sm">
          <span className="font-medium">{entry.entry_type.replace(/_/g, " ")}</span> — {entry.body}
          <div className="mt-1 text-xs text-muted-foreground">{new Date(entry.created_at).toLocaleString()}</div>
        </li>
      ))}
    </ul>
  );
}
