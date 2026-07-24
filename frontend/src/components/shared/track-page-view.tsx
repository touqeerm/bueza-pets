"use client";

import { useEffect } from "react";

import { trackEvent, type AnalyticsEventName } from "@/lib/analytics";

export function TrackPageView({ event }: { event: AnalyticsEventName }) {
  useEffect(() => {
    trackEvent(event);
  }, [event]);

  return null;
}
