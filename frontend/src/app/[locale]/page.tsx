"use client";

import { useEffect } from "react";
import { useTranslations } from "next-intl";

import { useRouter } from "@/i18n/navigation";

export default function SplashPage() {
  const router = useRouter();
  const t = useTranslations("splash");

  useEffect(() => {
    const timer = setTimeout(() => {
      router.replace("/language");
    }, 1500);
    return () => clearTimeout(timer);
  }, [router]);

  return (
    <main
      className="flex flex-1 flex-col items-center justify-center gap-4 px-6 text-center"
      onClick={() => router.replace("/language")}
    >
      <h1 className="text-4xl font-bold tracking-tight">{t("title")}</h1>
      <p className="text-lg text-muted-foreground">{t("tagline")}</p>
    </main>
  );
}
