"use client";

import { useTransition } from "react";
import { useLocale, useTranslations } from "next-intl";

import { usePathname, useRouter } from "@/i18n/navigation";
import { routing, type AppLocale } from "@/i18n/routing";
import { LOCALE_METADATA } from "@/i18n/locale-metadata";
import { cn } from "@/lib/utils";

export function LanguageSelector() {
  const t = useTranslations("languageSelector");
  const locale = useLocale();
  const pathname = usePathname();
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  function handleSelect(nextLocale: AppLocale) {
    if (nextLocale === locale) return;
    startTransition(() => {
      router.replace(pathname, { locale: nextLocale });
    });
  }

  return (
    <div
      role="radiogroup"
      aria-label={t("label")}
      className="flex w-full max-w-xs flex-col gap-2"
    >
      {routing.locales.map((loc) => {
        const isActive = loc === locale;
        return (
          <button
            key={loc}
            type="button"
            role="radio"
            aria-checked={isActive}
            disabled={isPending}
            onClick={() => handleSelect(loc)}
            className={cn(
              "flex items-center justify-between rounded-lg border px-4 py-3 text-left text-sm font-medium transition-colors disabled:opacity-50",
              isActive
                ? "border-primary bg-primary/10 text-primary"
                : "border-border hover:bg-muted",
            )}
          >
            <span>{LOCALE_METADATA[loc].nativeName}</span>
            {isActive ? <span aria-hidden="true">✓</span> : null}
          </button>
        );
      })}
    </div>
  );
}
