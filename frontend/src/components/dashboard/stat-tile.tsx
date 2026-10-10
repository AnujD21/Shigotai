import type { LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/card";
import { CountUp } from "@/components/motion/count-up";

export function StatTile({
  icon: Icon,
  label,
  value,
}: {
  icon: LucideIcon;
  label: string;
  value: number;
}) {
  return (
    <Card className="group flex h-full flex-col p-5 transition-[transform,box-shadow] duration-300 hover:-translate-y-0.5 hover:shadow-[var(--shadow-md)]">
      <div className="flex items-start justify-between gap-3">
        <p className="text-[13px] font-medium leading-snug text-[var(--color-text-secondary)]">{label}</p>
        <div className="flex size-7 shrink-0 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)] transition-colors group-hover:bg-[var(--color-accent-subtle)]">
          <Icon
            className="size-3.5 text-[var(--color-text-tertiary)] transition-colors group-hover:text-[var(--color-accent)]"
            aria-hidden
          />
        </div>
      </div>
      {/* mt-auto keeps numbers on one baseline when a label wraps to two lines. */}
      <CountUp
        value={value}
        className="mt-auto block pt-3 font-display text-[30px] font-semibold leading-none tabular-nums tracking-tight text-[var(--color-text-primary)]"
      />
    </Card>
  );
}
