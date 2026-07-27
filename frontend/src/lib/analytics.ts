// The full set of trackable events. Add a new one here, then call
// trackEvent() with it wherever it happens — no other wiring needed.
export type AnalyticsEventName =
  | "app_opened"
  | "language_selected"
  | "phone_entered"
  | "otp_requested"
  | "otp_verified"
  | "onboarding_completed"
  | "home_loaded"
  | "describe_problem_clicked"
  | "problem_submitted"
  | "vet_booking_started"
  | "vet_booking_completed"
  | "consultation_completed";

export function trackEvent(
  eventName: AnalyticsEventName,
  properties: Record<string, unknown> = {},
  userId?: number,
): void {
  fetch("/api/analytics/events", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ event_name: eventName, properties, user_id: userId ?? null }),
    keepalive: true,
  }).catch(() => undefined);
}
