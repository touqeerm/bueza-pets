import { getTranslations } from "next-intl/server";

import { PlaceholderScreen } from "@/components/shared/placeholder-screen";

export default async function Page() {
  const t = await getTranslations("home");
  return <PlaceholderScreen title={t("title")} description={t("subtitle")} />;
}
