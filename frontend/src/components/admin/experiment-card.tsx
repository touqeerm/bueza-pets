import Link from "next/link";

import { ExperimentStatusBadge } from "@/components/admin/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Experiment } from "@/lib/admin-types";

export function ExperimentCard({ experiment }: { experiment: Experiment }) {
  const primaryMetric = experiment.metrics.find((metric) => !metric.is_guardrail) ?? experiment.metrics[0];

  return (
    <Link href={`/admin/experiments/${experiment.id}`}>
      <Card className="transition-colors hover:border-ring">
        <CardHeader className="flex-row items-center justify-between gap-2">
          <CardTitle>{experiment.title}</CardTitle>
          <ExperimentStatusBadge status={experiment.status} />
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            We believe {experiment.hypothesis.action} for {experiment.hypothesis.persona} will result in{" "}
            {experiment.hypothesis.outcome}.
          </p>
          {primaryMetric?.latest_run ? (
            <p className="text-sm">
              <span className="font-medium">{primaryMetric.name}:</span> {primaryMetric.latest_run.current_value} (n=
              {primaryMetric.latest_run.sample_size}) — {primaryMetric.latest_run.recommendation}
            </p>
          ) : null}
        </CardContent>
      </Card>
    </Link>
  );
}
