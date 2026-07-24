"use client";

import { buttonVariants } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";
import { trackEvent } from "@/lib/analytics";

export function DescribeProblemLink({ label }: { label: string }) {
  return (
    <Link
      href="/describe-problem"
      onClick={() => trackEvent("describe_problem_clicked")}
      className={buttonVariants({ size: "lg", className: "w-full max-w-xs" })}
    >
      {label}
    </Link>
  );
}
