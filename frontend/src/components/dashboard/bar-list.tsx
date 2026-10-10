"use client";

import { motion, useReducedMotion } from "framer-motion";

export function BarList({ items }: { items: { label: string; value: number }[] }) {
  const max = Math.max(...items.map((item) => item.value), 1);
  const reduce = useReducedMotion();

  return (
    <ul className="space-y-3.5">
      {items.map((item, i) => {
        const fraction = item.value > 0 ? Math.max(0.04, item.value / max) : 0;
        return (
          <li key={item.label} className="flex items-center gap-3">
            <span className="w-36 shrink-0 truncate text-[13px] text-[var(--color-text-secondary)]" title={item.label}>
              {item.label}
            </span>
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-[var(--color-accent-subtle)]">
              <motion.div
                className="h-full origin-left rounded-full bg-[var(--color-accent)]"
                initial={{ scaleX: reduce ? fraction : 0 }}
                whileInView={{ scaleX: fraction }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: 0.05 * i, ease: [0.16, 1, 0.3, 1] }}
              />
            </div>
            <span className="w-6 shrink-0 text-right text-[13px] font-medium tabular-nums text-[var(--color-text-primary)]">
              {item.value}
            </span>
          </li>
        );
      })}
    </ul>
  );
}
