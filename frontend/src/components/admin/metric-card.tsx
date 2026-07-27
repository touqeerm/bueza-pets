import { MetricStatusBadge } from "@/components/admin/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Metric } from "@/lib/admin-types";

export function MetricCard({ metric }: { metric: Metric }) {
  const run = metric.latest_run;
  return (
    <Card className="p-4">
      <CardHeader className="flex-row items-center justify-between gap-2">
        <CardTitle>
          {metric.name}
          {metric.is_guardrail ? <span className="ml-1 text-xs font-normal text-muted-foreground">(guardrail)</span> : null}
        </CardTitle>
        <MetricStatusBadge status={run?.status ?? "insufficient_data"} />
      </CardHeader>
      <CardContent>
        <p className="text-xs text-muted-foreground">
          target {metric.target_value} · min sample {metric.minimum_sample_size}
        </p>
        {run ? (
          <>
            <p className="text-lg font-semibold">
              {run.current_value} <span className="text-sm font-normal text-muted-foreground">(n={run.sample_size})</span>
            </p>
            <p className="text-sm text-muted-foreground">{run.recommendation}</p>
          </>
        ) : (
          <p className="text-sm text-muted-foreground">No evaluation yet.</p>
        )}
      </CardContent>
    </Card>
  );
}
