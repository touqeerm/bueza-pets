import { randomUUID } from "node:crypto";

import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { getBackendApiUrl } from "@/lib/backend";

const ANONYMOUS_ID_COOKIE_NAME = "analytics_id";
const ANONYMOUS_ID_MAX_AGE_SECONDS = 60 * 60 * 24 * 365;

export async function POST(request: Request) {
  const body = await request.json();
  const cookieStore = await cookies();

  let anonymousId = cookieStore.get(ANONYMOUS_ID_COOKIE_NAME)?.value;
  if (!anonymousId) {
    anonymousId = randomUUID();
    cookieStore.set(ANONYMOUS_ID_COOKIE_NAME, anonymousId, {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
      maxAge: ANONYMOUS_ID_MAX_AGE_SECONDS,
    });
  }

  await fetch(`${getBackendApiUrl()}/analytics/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...body, anonymous_id: anonymousId }),
  }).catch(() => undefined);

  return NextResponse.json({ ok: true });
}
