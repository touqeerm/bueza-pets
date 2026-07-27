import type {
  DashboardSnapshot,
  EventMappingRole,
  Experiment,
  Hypothesis,
  JournalEntry,
  JournalEntryType,
  Metric,
  MetricKind,
} from "@/lib/admin-types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/admin/${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed (${response.status})`);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export function getDashboard(): Promise<DashboardSnapshot> {
  return request("dashboard");
}

export function listExperiments(): Promise<Experiment[]> {
  return request("experiments");
}

export function getExperiment(id: number): Promise<Experiment> {
  return request(`experiments/${id}`);
}

export function createExperiment(input: {
  title: string;
  hypothesis: Hypothesis;
  evaluation_window_days: number;
}): Promise<Experiment> {
  return request("experiments", { method: "POST", body: JSON.stringify(input) });
}

export function addMetric(
  experimentId: number,
  input: {
    name: string;
    kind: MetricKind;
    is_guardrail: boolean;
    target_value: number;
    minimum_sample_size: number;
    event_mappings: { role: EventMappingRole; event_name: string; property_filters: Record<string, unknown> }[];
  },
): Promise<Metric> {
  return request(`experiments/${experimentId}/metrics`, { method: "POST", body: JSON.stringify(input) });
}

export function startExperiment(id: number): Promise<Experiment> {
  return request(`experiments/${id}/start`, { method: "POST" });
}

export function evaluateExperiment(id: number): Promise<Experiment> {
  return request(`experiments/${id}/evaluate`, { method: "POST" });
}

export function archiveExperiment(id: number): Promise<Experiment> {
  return request(`experiments/${id}/archive`, { method: "POST" });
}

export function listJournalEntries(experimentId?: number): Promise<JournalEntry[]> {
  return request(`journal-entries${experimentId ? `?experiment_id=${experimentId}` : ""}`);
}

export function addJournalEntry(input: {
  entry_type: JournalEntryType;
  body: string;
  experiment_id: number | null;
}): Promise<JournalEntry> {
  return request("journal-entries", { method: "POST", body: JSON.stringify(input) });
}
