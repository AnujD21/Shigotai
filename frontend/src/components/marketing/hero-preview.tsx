"use client";

import { motion } from "framer-motion";
import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const ROWS = [
  { icon: CheckCircle2, tone: "text-[var(--color-success)]", label: "Python", detail: "Meets stated requirement" },
  { icon: CheckCircle2, tone: "text-[var(--color-success)]", label: "Computer Vision", detail: "PyTorch, OpenCV, YOLO" },
  { icon: AlertTriangle, tone: "text-[var(--color-warning)]", label: "JLPT N2", detail: "You have N3" },
  { icon: XCircle, tone: "text-[var(--color-text-tertiary)]", label: "AWS", detail: "Not on your profile" },
];

export function HeroPreview() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      className="w-full max-w-md rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-[var(--shadow-lg)]"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[12.5px] font-medium text-[var(--color-text-secondary)]">Kaede Robotics &middot; Yokohama</p>
          {/* Decorative product preview, not document content -- intentionally not a heading element so it doesn't disrupt the page's heading outline. */}
          <p className="mt-0.5 text-[17px] font-semibold text-[var(--color-text-primary)]">Computer Vision Engineer</p>
        </div>
        <Badge tone="success">Strong match</Badge>
      </div>

      <div className="mt-2 flex items-center gap-1.5 text-[12.5px] text-[var(--color-success)]">
        <span className="relative flex size-1.5">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[var(--color-success)] opacity-50" />
          <span className="relative inline-flex size-1.5 rounded-full bg-[var(--color-success)]" />
        </span>
        Verified active &middot; 3 hours ago
      </div>

      <div className="mt-5 space-y-3 border-t border-[var(--color-border)] pt-4">
        {ROWS.map((row, i) => (
          <motion.div
            key={row.label}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.35, delay: 0.15 + i * 0.08 }}
            className="flex items-start gap-2.5 text-[13.5px]"
          >
            <row.icon className={`size-4 shrink-0 ${row.tone}`} aria-hidden />
            <div>
              <span className="text-[var(--color-text-primary)]">{row.label}</span>
              <span className="ml-2 text-[12.5px] text-[var(--color-text-tertiary)]">{row.detail}</span>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-5 rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)] px-3.5 py-3 text-[12.5px] leading-relaxed text-[var(--color-text-secondary)]">
        You meet 2 of the stated requirements, including Python and Computer Vision. Your JLPT is one level below what&apos;s
        listed, and AWS isn&apos;t on your profile yet.
      </div>
    </motion.div>
  );
}
