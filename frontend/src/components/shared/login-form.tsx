"use client";

import { useEffect, useState, type FormEvent } from "react";
import { Loader2 } from "lucide-react";
import { useTranslations } from "next-intl";

import { Button } from "@/components/ui/button";
import { useRouter } from "@/i18n/navigation";
import { trackEvent } from "@/lib/analytics";

type Step = "phone" | "otp";

const inputClassName =
  "h-12 rounded-lg border border-border bg-background px-4 text-base outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50";

export function LoginForm() {
  const t = useTranslations("login");
  const router = useRouter();

  const [step, setStep] = useState<Step>("phone");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [code, setCode] = useState("");
  const [mockOtp, setMockOtp] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    trackEvent("login_started");
  }, []);

  async function handleRequestOtp(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const response = await fetch("/api/auth/otp/request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone_number: phoneNumber }),
      });
      if (!response.ok) throw new Error();
      const data = await response.json();
      setMockOtp(data.otp_code);
      setStep("otp");
    } catch {
      setError(t("requestError"));
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleVerifyOtp(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const response = await fetch("/api/auth/otp/verify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone_number: phoneNumber, code }),
      });
      if (!response.ok) throw new Error();
      const data = await response.json();
      trackEvent("login_completed", {}, data.user?.id);
      router.replace("/home");
    } catch {
      setError(t("verifyError"));
    } finally {
      setIsSubmitting(false);
    }
  }

  if (step === "phone") {
    return (
      <form onSubmit={handleRequestOtp} className="flex w-full max-w-xs flex-col gap-3">
        <label htmlFor="phone-number" className="text-left text-sm font-medium">
          {t("phoneLabel")}
        </label>
        <input
          id="phone-number"
          type="tel"
          required
          value={phoneNumber}
          onChange={(event) => setPhoneNumber(event.target.value)}
          placeholder={t("phonePlaceholder")}
          className={inputClassName}
        />
        {error ? (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        ) : null}
        <Button type="submit" disabled={isSubmitting} size="lg" className="w-full">
          {isSubmitting ? <Loader2 data-icon="inline-start" className="animate-spin" /> : null}
          {t("sendOtpButton")}
        </Button>
      </form>
    );
  }

  return (
    <form onSubmit={handleVerifyOtp} className="flex w-full max-w-xs flex-col gap-3">
      <label htmlFor="otp-code" className="text-left text-sm font-medium">
        {t("otpLabel")}
      </label>
      <input
        id="otp-code"
        type="text"
        inputMode="numeric"
        required
        value={code}
        onChange={(event) => setCode(event.target.value)}
        placeholder={t("otpPlaceholder")}
        className={`${inputClassName} tracking-widest`}
      />
      {mockOtp ? <p className="text-xs text-muted-foreground">{t("mockOtpHint", { code: mockOtp })}</p> : null}
      {error ? (
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
      ) : null}
      <Button type="submit" disabled={isSubmitting} size="lg" className="w-full">
        {isSubmitting ? <Loader2 data-icon="inline-start" className="animate-spin" /> : null}
        {t("verifyButton")}
      </Button>
    </form>
  );
}
