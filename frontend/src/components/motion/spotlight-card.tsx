"use client";

import { forwardRef, type HTMLAttributes, type PointerEvent } from "react";
import { cn } from "@/lib/utils";

/**
 * A container whose border glows where the cursor is (see `.spotlight` in
 * globals.css). Position is written to CSS variables directly, so moving the
 * mouse never re-renders React.
 */
export function trackSpotlight(event: PointerEvent<HTMLElement>) {
  const rect = event.currentTarget.getBoundingClientRect();
  event.currentTarget.style.setProperty("--spot-x", `${event.clientX - rect.left}px`);
  event.currentTarget.style.setProperty("--spot-y", `${event.clientY - rect.top}px`);
}

export const SpotlightCard = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, onPointerMove, ...props }, ref) => {
    function handlePointerMove(event: PointerEvent<HTMLDivElement>) {
      trackSpotlight(event);
      onPointerMove?.(event);
    }
    return <div ref={ref} className={cn("spotlight", className)} onPointerMove={handlePointerMove} {...props} />;
  }
);
SpotlightCard.displayName = "SpotlightCard";
