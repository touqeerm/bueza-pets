import { ExperimentDetailView } from "@/components/admin/experiment-detail-view";

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function Page({ params }: PageProps) {
  const { id } = await params;
  return <ExperimentDetailView experimentId={Number(id)} />;
}
