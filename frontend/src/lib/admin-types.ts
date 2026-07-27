export type ExperimentStatus =
  | "draft"
  | "running"
  | "evaluating"
  | "validated"
  | "invalidated"
  | "inconclusive"
  | "archived";

export type MetricStatus = "insufficient_data" | "on_track" | "met_target" | "missed_target" | "at_risk";

export type MetricKind = "conversion_rate" | "count" | "ratio";

export type EventMappingRole = "numerator" | "denominator" | "count_target";

export type JournalEntryType = "observation" | "decision" | "pivot_consideration" | "note";

export type Hypothesis = {
  action: string;
  persona: string;
  outcome: string;
  signal: string;
};

export type EventMapping = {
  id: number;
  role: EventMappingRole;
  event_name: string;
  property_filters: Record<string, unknown>;
};

// target_value/current_value arrive as strings — FastAPI/Pydantic serialize
// Decimal fields as JSON strings to preserve precision.
export type EvaluationRun = {
  id: number;
  ran_at: string;
  sample_size: number;
  current_value: string;
  status: MetricStatus;
  recommendation: string;
};

export type Metric = {
  id: number;
  name: string;
  kind: MetricKind;
  is_guardrail: boolean;
  target_value: string;
  minimum_sample_size: number;
  event_mappings: EventMapping[];
  latest_run: EvaluationRun | null;
};

export type Experiment = {
  id: number;
  title: string;
  status: ExperimentStatus;
  hypothesis: Hypothesis;
  evaluation_window_days: number;
  started_at: string | null;
  ended_at: string | null;
  created_at: string;
  metrics: Metric[];
};

export type JournalEntry = {
  id: number;
  experiment_id: number | null;
  entry_type: JournalEntryType;
  body: string;
  created_at: string;
};

export type DashboardSnapshot = {
  running: Experiment[];
  needs_decision: Experiment[];
  recent_journal_entries: JournalEntry[];
};

// Mirrors the backend's EventName enum (app/domain/events.py) — the single
// source of truth is the backend; this list just needs to stay in sync since
// there's no shared package between the two services.
export const TRACKABLE_EVENTS = [
  "app_opened",
  "language_selected",
  "phone_entered",
  "otp_requested",
  "otp_verified",
  "onboarding_completed",
  "home_loaded",
  "describe_problem_clicked",
  "problem_submitted",
  "vet_booking_started",
  "vet_booking_completed",
  "consultation_completed",
] as const;

export const METRIC_KINDS: MetricKind[] = ["conversion_rate", "ratio", "count"];

export const JOURNAL_ENTRY_TYPES: JournalEntryType[] = ["observation", "decision", "pivot_consideration", "note"];
