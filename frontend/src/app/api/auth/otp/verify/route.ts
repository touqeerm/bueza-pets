import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { isSecureCookieEnabled, SESSION_COOKIE_NAME, SESSION_MAX_AGE_SECONDS } from "@/lib/auth";
import { getBackendApiUrl } from "@/lib/backend";

export async function POST(request: Request) {
  const body = await request.json();

  const backendResponse = await fetch(`${getBackendApiUrl()}/auth/otp/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await backendResponse.json();

  if (!backendResponse.ok) {
    return NextResponse.json(data, { status: backendResponse.status });
  }

  const cookieStore = await cookies();
  cookieStore.set(SESSION_COOKIE_NAME, data.access_token, {
    httpOnly: true,
    secure: isSecureCookieEnabled(),
    sameSite: "lax",
    path: "/",
    maxAge: SESSION_MAX_AGE_SECONDS,
  });

  return NextResponse.json({ user: data.user });
}
