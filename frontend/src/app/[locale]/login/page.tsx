import { getTranslations } from "next-intl/server";

import { LoginForm } from "@/components/shared/login-form";

export default async function Page() {
  const t = await getTranslations("login");

  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-6 px-6 text-center">
      <div className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold">{t("title")}</h1>
        <p className="text-muted-foreground">{t("subtitle")}</p>
      </div>
      <LoginForm />
    </main>
  );
}
