import createMiddleware from "next-intl/middleware";

import { routing } from "./i18n/routing";

export default createMiddleware(routing);

export const config = {
  // "admin" is excluded alongside "api": Mission Control is an internal,
  // English-only tool and deliberately lives outside the farmer-facing
  // [locale] route tree, so it shouldn't be redirected to /en/admin.
  matcher: ["/((?!api|admin|_next|_vercel|.*\\..*).*)"],
};
