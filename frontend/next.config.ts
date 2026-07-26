import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const nextConfig: NextConfig = {
  // Produces a self-contained server bundle (.next/standalone) so the
  // Docker image doesn't need to ship node_modules or the full source tree.
  output: "standalone",
};

export default withNextIntl(nextConfig);
