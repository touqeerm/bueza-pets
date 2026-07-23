import { routing, type AppLocale } from "./routing";

export const LOCALE_METADATA: Record<AppLocale, { englishName: string; nativeName: string }> = {
  en: { englishName: "English", nativeName: "English" },
  es: { englishName: "Spanish", nativeName: "Español" },
  fr: { englishName: "French", nativeName: "Français" },
};

export function isAppLocale(value: string): value is AppLocale {
  return (routing.locales as readonly string[]).includes(value);
}

export function getLocaleNativeName(locale: AppLocale): string {
  return LOCALE_METADATA[locale].nativeName;
}
