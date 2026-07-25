import type { AppLocale } from "./routing";

export const LOCALE_METADATA: Record<AppLocale, { englishName: string; nativeName: string }> = {
  en: { englishName: "English", nativeName: "English" },
  hi: { englishName: "Hindi", nativeName: "हिन्दी" },
  kn: { englishName: "Kannada", nativeName: "ಕನ್ನಡ" },
  te: { englishName: "Telugu", nativeName: "తెలుగు" },
  ta: { englishName: "Tamil", nativeName: "தமிழ்" },
};
