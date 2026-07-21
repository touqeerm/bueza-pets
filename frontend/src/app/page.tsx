"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function SplashPage() {
  const router = useRouter();

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
      <h1 className="text-4xl font-bold tracking-tight">Bueza Pets</h1>
      <p className="text-lg text-muted-foreground">Livestock care, one tap away</p>
    </main>
  );
}
