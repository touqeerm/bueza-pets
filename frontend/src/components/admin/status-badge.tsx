import { Badge } from "@/components/ui/badge";
import type { ExperimentStatus, MetricStatus } from "@/lib/admin-types";

type BadgeVariant = "default" | "secondary" | "outline" | "success" | "warning" | "destructive";

const EXPERIMENT_STATUS_VARIANT: Record<ExperimentStatus, BadgeVariant> = {
  draft: "outline",
  running: "default",
  evaluating: "warning",
  validated: "success",
  invalidated: "destructive",
  inconclusive: "secondary",
  archived: "outline",
};

const METRIC_STATUS_VARIANT: Record<MetricStatus, BadgeVariant> = {
  insufficient_data: "outline",
  on_track: "default",
  met_target: "success",
  missed_target: "destructive",
  at_risk: "destructive",
};

export function ExperimentStatusBadge({ status }: { status: ExperimentStatus }) {
  return <Badge variant={EXPERIMENT_STATUS_VARIANT[status]}>{status.replace(/_/g, " ")}</Badge>;
}

export function MetricStatusBadge({ status }: { status: MetricStatus }) {
  return <Badge variant={METRIC_STATUS_VARIANT[status]}>{status.replace(/_/g, " ")}</Badge>;
}
