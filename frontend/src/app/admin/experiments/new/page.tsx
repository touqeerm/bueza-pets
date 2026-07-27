import type { Metadata } from "next";

import { NewExperimentForm } from "@/components/admin/new-experiment-form";

export const metadata: Metadata = { title: "New Experiment" };

export default function Page() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-xl font-semibold">New experiment</h1>
      <NewExperimentForm />
    </div>
  );
}
