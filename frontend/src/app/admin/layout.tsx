import type { Metadata } from "next";
import type { ReactNode } from "react";
import Link from "next/link";
import { redirect } from "next/navigation";

import { routing } from "@/i18n/routing";
import { getCurrentUser } from "@/lib/admin-guard";

import "../globals.css";

export const metadata: Metadata = {
  title: { default: "Mission Control", template: "%s | Mission Control" },
};

export default async function AdminLayout({ children }: { children: ReactNode }) {
  const user = await getCurrentUser();
  if (!user) redirect(`/${routing.defaultLocale}/login`);
  if (!user.is_admin) redirect(`/${routing.defaultLocale}/home`);

  return (
    <html lang="en" className="h-full antialiased">
      <body className="flex min-h-full flex-col bg-background text-foreground">
        <header className="flex items-center gap-4 border-b border-border px-6 py-3">
          <Link href="/admin" className="text-sm font-semibold">
            Mission Control
          </Link>
          <nav className="flex gap-4 text-sm text-muted-foreground">
            <Link href="/admin" className="hover:text-foreground">
              Dashboard
            </Link>
            <Link href="/admin/journal" className="hover:text-foreground">
              Journal
            </Link>
          </nav>
        </header>
        <main className="flex flex-1 flex-col gap-6 p-6">{children}</main>
      </body>
    </html>
  );
}
