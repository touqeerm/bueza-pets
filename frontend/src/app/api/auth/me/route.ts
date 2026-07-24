import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { getBackendApiUrl, SESSION_COOKIE_NAME } from "@/lib/auth";

export async function GET() {
  const token = (await cookies()).get(SESSION_COOKIE_NAME)?.value;

  if (!token) {
    return NextResponse.json({ user: null }, { status: 401 });
  }

  const backendResponse = await fetch(`${getBackendApiUrl()}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!backendResponse.ok) {
    return NextResponse.json({ user: null }, { status: 401 });
  }

  const user = await backendResponse.json();
  return NextResponse.json({ user });
}
