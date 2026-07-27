import { cookies } from "next/headers";
import { type NextRequest, NextResponse } from "next/server";

import { SESSION_COOKIE_NAME } from "@/lib/auth";
import { getBackendApiUrl } from "@/lib/backend";

// A single catch-all proxy for every /admin/* backend route, rather than one
// route handler file per endpoint — the backend already owns validation and
// the admin-only guard (403 via require_admin_user), so this layer is pure
// cookie-to-bearer-token translation, nothing more.
async function proxy(request: NextRequest, path: string[]): Promise<NextResponse> {
  const token = (await cookies()).get(SESSION_COOKIE_NAME)?.value;
  if (!token) {
    return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
  }

  const targetUrl = new URL(`${getBackendApiUrl()}/admin/${path.join("/")}`);
  targetUrl.search = request.nextUrl.search;

  const hasBody = request.method !== "GET" && request.method !== "DELETE";
  const backendResponse = await fetch(targetUrl, {
    method: request.method,
    headers: {
      Authorization: `Bearer ${token}`,
      ...(hasBody ? { "Content-Type": "application/json" } : {}),
    },
    body: hasBody ? await request.text() : undefined,
    cache: "no-store",
  });

  const responseText = await backendResponse.text();
  return new NextResponse(responseText || null, {
    status: backendResponse.status,
    headers: { "Content-Type": backendResponse.headers.get("Content-Type") ?? "application/json" },
  });
}

type RouteContext = { params: Promise<{ path: string[] }> };

export async function GET(request: NextRequest, context: RouteContext) {
  return proxy(request, (await context.params).path);
}

export async function POST(request: NextRequest, context: RouteContext) {
  return proxy(request, (await context.params).path);
}

export async function PATCH(request: NextRequest, context: RouteContext) {
  return proxy(request, (await context.params).path);
}

export async function DELETE(request: NextRequest, context: RouteContext) {
  return proxy(request, (await context.params).path);
}
