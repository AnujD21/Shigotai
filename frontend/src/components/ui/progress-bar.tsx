"use client";

import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";

export function ProgressBar({ value, className, trackClassName }: { value: number; className?: string; trackClassName?: string }) {
  const clamped = Math.max(0, Math.min(100, value));
  const reduce = useReducedMotion();
  return (
    <div
      className={cn("h-1.5 w-full overflow-hidden rounded-full bg-[var(--color-bg-subtle)]", trackClassName)}
      role="progressbar"
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      {/* scaleX rather than width: animates on the compositor, no layout. */}
      <motion.div
        className={cn("h-full origin-left rounded-full bg-[var(--color-accent)]", className)}
        initial={{ scaleX: reduce ? clamped / 100 : 0 }}
        animate={{ scaleX: clamped / 100 }}
        transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1], delay: 0.15 }}
      />
    </div>
  );
}
