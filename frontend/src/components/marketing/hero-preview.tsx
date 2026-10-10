"use client";

import { motion, useMotionValue, useReducedMotion, useSpring, useTransform, type Variants } from "framer-motion";
import { AlertTriangle, BellRing, CheckCircle2, XCircle } from "lucide-react";
import type { PointerEvent } from "react";
import { Badge } from "@/components/ui/badge";
import { EASE_OUT_EXPO } from "@/components/motion/fade-in";

type RowState = "match" | "partial" | "missing";

const ROWS: { state: RowState; label: string; detail: string }[] = [
  { state: "match", label: "Python", detail: "Meets stated requirement" },
  { state: "match", label: "Computer Vision", detail: "PyTorch, OpenCV, YOLO" },
  { state: "match", label: "2+ years experience", detail: "You have 2.5" },
  { state: "partial", label: "JLPT N2", detail: "You have N3 -- one level below" },
  { state: "missing", label: "AWS", detail: "Not on your profile yet" },
];

const STATE_STYLE: Record<RowState, { icon: typeof CheckCircle2; text: string; bar: string }> = {
  match: { icon: CheckCircle2, text: "text-[var(--color-success)]", bar: "bg-[var(--color-success)]" },
  partial: { icon: AlertTriangle, text: "text-[var(--color-warning)]", bar: "bg-[var(--color-warning)]" },
  missing: { icon: XCircle, text: "text-[var(--color-text-tertiary)]", bar: "bg-[var(--color-border-strong)]" },
};

const ROWS_START = 0.55;
const ROW_STEP = 0.14;

/**
 * Illustrative product preview: a match card that assembles itself the way
 * the engine works -- requirement by requirement, no single mystery score --
 * then an alert slides in. Tilts toward the cursor on desktop.
 */
export function HeroPreview() {
  const reduce = useReducedMotion();
  const px = useMotionValue(0);
  const py = useMotionValue(0);
  const rotateX = useSpring(useTransform(py, [-0.5, 0.5], [5, -5]), { stiffness: 150, damping: 18 });
  const rotateY = useSpring(useTransform(px, [-0.5, 0.5], [-7, 7]), { stiffness: 150, damping: 18 });

  function handlePointerMove(event: PointerEvent<HTMLDivElement>) {
    if (reduce || event.pointerType !== "mouse") return;
    const rect = event.currentTarget.getBoundingClientRect();
    px.set((event.clientX - rect.left) / rect.width - 0.5);
    py.set((event.clientY - rect.top) / rect.height - 0.5);
  }

  const rowVariants: Variants = {
    hidden: { opacity: 0, x: reduce ? 0 : -8 },
    show: (i: number) => ({
      opacity: 1,
      x: 0,
      transition: { delay: reduce ? 0 : ROWS_START + i * ROW_STEP, duration: 0.45, ease: EASE_OUT_EXPO },
    }),
  };

  return (
    <div
      className="relative w-full max-w-[440px] [perspective:1200px]"
      onPointerMove={handlePointerMove}
      onPointerLeave={() => {
        px.set(0);
        py.set(0);
      }}
    >
      <motion.div
        style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
        initial={{ opacity: 0, y: reduce ? 0 : 24, scale: reduce ? 1 : 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.9, delay: reduce ? 0 : 0.2, ease: EASE_OUT_EXPO }}
        className="relative rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-[0_30px_80px_-30px_rgb(80_30_20/0.35),var(--shadow-md)]"
      >
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-[12.5px] font-medium text-[var(--color-text-secondary)]">Kaede Robotics &middot; Yokohama</p>
            {/* Decorative product preview, not document content -- intentionally not a heading element. */}
            <p className="mt-0.5 font-display text-[19px] font-semibold text-[var(--color-text-primary)]">
              Computer Vision Engineer
            </p>
          </div>
          <motion.div
            initial={{ opacity: 0, scale: reduce ? 1 : 0.85 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: "spring", stiffness: 300, damping: 18, delay: reduce ? 0 : ROWS_START + ROWS.length * ROW_STEP }}
          >
            <Badge tone="success">Strong match</Badge>
          </motion.div>
        </div>

        <div className="mt-2 flex items-center gap-1.5 text-[12.5px] text-[var(--color-success)]">
          <span className="relative flex size-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[var(--color-success)] opacity-50" />
            <span className="relative inline-flex size-1.5 rounded-full bg-[var(--color-success)]" />
          </span>
          Verified active &middot; 3 hours ago
        </div>

        {/* Requirements met: one segment per requirement, filled in order. */}
        <div className="mt-5">
          <div className="mb-2 flex items-baseline justify-between text-[12px]">
            <span className="font-medium text-[var(--color-text-secondary)]">Stated requirements</span>
            <span className="tabular-nums text-[var(--color-text-tertiary)]">3 met &middot; 1 close &middot; 1 missing</span>
          </div>
          <div className="flex gap-1">
            {ROWS.map((row, i) => (
              <div key={row.label} className="h-1.5 flex-1 overflow-hidden rounded-full bg-[var(--color-bg-subtle)]">
                <motion.div
                  className={`h-full origin-left rounded-full ${STATE_STYLE[row.state].bar}`}
                  initial={{ scaleX: reduce ? 1 : 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{ delay: reduce ? 0 : ROWS_START + i * ROW_STEP, duration: 0.4, ease: EASE_OUT_EXPO }}
                />
              </div>
            ))}
          </div>
        </div>

        <ul className="mt-4 space-y-2.5 border-t border-[var(--color-border)] pt-4">
          {ROWS.map((row, i) => {
            const style = STATE_STYLE[row.state];
            return (
              <motion.li
                key={row.label}
                custom={i}
                variants={rowVariants}
                initial="hidden"
                animate="show"
                className="flex items-center gap-2.5 text-[13.5px]"
              >
                <style.icon className={`size-4 shrink-0 ${style.text}`} aria-hidden />
                <span className="text-[var(--color-text-primary)]">{row.label}</span>
                <span className="truncate text-[12.5px] text-[var(--color-text-tertiary)]">{row.detail}</span>
              </motion.li>
            );
          })}
        </ul>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: reduce ? 0 : ROWS_START + ROWS.length * ROW_STEP + 0.15, duration: 0.6 }}
          className="mt-5 rounded-[10px] bg-[var(--color-bg-subtle)] px-3.5 py-3 text-[12.5px] leading-relaxed text-[var(--color-text-secondary)]"
        >
          You meet the core technical requirements. Your JLPT is one level below what&apos;s listed, and AWS
          isn&apos;t on your profile yet.
        </motion.p>
      </motion.div>

      {/* Alert that "arrives" after the card is built. */}
      <motion.div
        initial={{ opacity: 0, y: reduce ? 0 : 16, scale: reduce ? 1 : 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ type: "spring", stiffness: 220, damping: 20, delay: reduce ? 0 : 1.75 }}
        className="absolute -bottom-7 -left-3 sm:-left-10"
      >
        <motion.div
          animate={reduce ? undefined : { y: [0, -5, 0] }}
          transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 2.4 }}
          className="flex items-center gap-3 rounded-[14px] border border-[var(--color-border)] bg-[var(--color-surface-raised)]/95 py-2.5 pl-3 pr-4 shadow-[var(--shadow-lg)] backdrop-blur-sm"
        >
          <span className="flex size-8 items-center justify-center rounded-[10px] bg-[var(--color-accent-subtle)]">
            <BellRing className="size-4 text-[var(--color-accent)]" aria-hidden />
          </span>
          <span>
            <span className="block text-[12.5px] font-semibold text-[var(--color-text-primary)]">New match for you</span>
            <span className="block text-[12px] text-[var(--color-text-tertiary)]">ML Engineer &middot; Hikari Systems, Tokyo</span>
          </span>
        </motion.div>
      </motion.div>
    </div>
  );
}
