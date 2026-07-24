import { getTranslations } from "next-intl/server";

import { DescribeProblemLink } from "@/components/shared/describe-problem-link";
import { TrackPageView } from "@/components/shared/track-page-view";

export default async function Page() {
  const t = await getTranslations("home");

  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-6 px-6 text-center">
      <TrackPageView event="home_loaded" />
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold">{t("title")}</h1>
        <p className="text-muted-foreground">{t("subtitle")}</p>
      </div>
      <DescribeProblemLink label={t("describeProblemCta")} />
    </main>
  );
}
