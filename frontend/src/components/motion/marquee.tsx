"use client";

import { useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

/**
 * Infinite horizontal scroll of `items`, pausing on hover. Pure CSS
 * transform animation (runs on the compositor). With reduced motion it
 * becomes a static, wrapping row.
 */
export function Marquee({
  items,
  className,
  durationSeconds = 40,
}: {
  items: ReactNode[];
  className?: string;
  durationSeconds?: number;
}) {
  const reduce = useReducedMotion();

  if (reduce) {
    return <div className={cn("flex flex-wrap justify-center gap-x-10 gap-y-3", className)}>{items}</div>;
  }

  return (
    <div className={cn("fade-x group overflow-hidden", className)}>
      <div
        className="flex w-max animate-marquee gap-x-12 group-hover:[animation-play-state:paused]"
        style={{ ["--marquee-duration" as string]: `${durationSeconds}s` }}
      >
        {/* Two copies so translating by -50% loops seamlessly. */}
        {[0, 1].map((copy) => (
          <div key={copy} className="flex shrink-0 items-center gap-x-12" aria-hidden={copy === 1}>
            {items}
          </div>
        ))}
      </div>
    </div>
  );
}
