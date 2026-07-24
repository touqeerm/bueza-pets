import { NextResponse } from "next/server";

import { getBackendApiUrl } from "@/lib/backend";

export async function POST(request: Request) {
  const body = await request.json();

  const backendResponse = await fetch(`${getBackendApiUrl()}/auth/otp/request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await backendResponse.json();
  return NextResponse.json(data, { status: backendResponse.status });
}
