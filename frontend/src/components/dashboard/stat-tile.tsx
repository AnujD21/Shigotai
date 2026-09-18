import type { LucideIcon } from "lucide-react";
import { Card } from "@/components/ui/card";

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
    <Card className="p-5">
      <div className="flex items-center justify-between gap-3">
        <p className="text-[13px] font-medium text-[var(--color-text-secondary)]">{label}</p>
        <div className="flex size-7 shrink-0 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)]">
          <Icon className="size-3.5 text-[var(--color-text-tertiary)]" aria-hidden />
        </div>
      </div>
      <p className="mt-3 text-[28px] font-semibold tracking-tight text-[var(--color-text-primary)]">{value}</p>
    </Card>
  );
}
