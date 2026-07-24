export const SESSION_COOKIE_NAME = "session_token";
export const SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 30;

// Not tied to NODE_ENV: `next start` always runs in production mode even
// when there's no TLS termination in front of it yet, and a Secure cookie
// set over plain HTTP is silently dropped by real browsers. Flip this on
// via COOKIE_SECURE=true once HTTPS is in place.
export function isSecureCookieEnabled(): boolean {
  return process.env.COOKIE_SECURE === "true";
}
