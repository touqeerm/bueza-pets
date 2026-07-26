import type { Metadata } from "next";
import { Rocket } from "lucide-react";
import Image from "next/image";
import { getTranslations, setRequestLocale } from "next-intl/server";

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

  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-6 px-6 text-center">
      <Image src="/logo.png" alt="Bueza Veterinary" width={72} height={72} className="rounded-2xl" />

      <div className="flex items-center gap-2 rounded-full border border-amber-300 bg-amber-100 px-5 py-2.5 dark:border-amber-400/30 dark:bg-amber-400/10">
        <Rocket className="size-5 text-amber-700 motion-safe:animate-pulse dark:text-amber-400" aria-hidden="true" />
        <span className="text-base font-bold tracking-wide text-amber-900 uppercase dark:text-amber-300">
          {t("comingSoonBadge")}
        </span>
      </div>

      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold">{t("title")}</h1>
        <p className="max-w-sm text-muted-foreground">{t("comingSoonMessage")}</p>
      </div>
    </main>
  );
}
