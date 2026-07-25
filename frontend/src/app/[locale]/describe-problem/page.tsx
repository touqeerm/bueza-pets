import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";

import { PlaceholderScreen } from "@/components/shared/placeholder-screen";

type PageProps = {
  params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("describeProblem");
  return { title: t("title") };
}

export default async function Page({ params }: PageProps) {
  const { locale } = await params;
  setRequestLocale(locale);
  const t = await getTranslations("describeProblem");
  return <PlaceholderScreen title={t("title")} description={t("subtitle")} />;
}
