// The full set of trackable events. Add a new one here, then call
// trackEvent() with it wherever it happens — no other wiring needed.
export type AnalyticsEventName =
  | "app_opened"
  | "language_selected"
  | "login_started"
  | "login_completed"
  | "home_loaded"
  | "describe_problem_clicked";

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
