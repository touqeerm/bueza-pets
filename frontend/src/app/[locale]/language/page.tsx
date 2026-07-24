import { getTranslations } from "next-intl/server";

import { LanguageSelector } from "@/components/shared/language-selector";
import { buttonVariants } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";

export default async function Page() {
  const t = await getTranslations("languageSelector");

  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-6 px-6 text-center">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold">{t("title")}</h1>
        <p className="text-muted-foreground">{t("subtitle")}</p>
      </div>
      <LanguageSelector />
      <Link
        href="/login"
        className={buttonVariants({ size: "lg", className: "w-full max-w-xs" })}
      >
        {t("continue")}
      </Link>
    </main>
  );
}
