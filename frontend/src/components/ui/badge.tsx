import { cn } from "@/lib/utils";

const TONES = {
  neutral: "bg-[var(--color-bg-subtle)] text-[var(--color-text-secondary)] border-[var(--color-border)]",
  accent: "bg-[var(--color-accent-subtle)] text-[var(--color-accent)] border-[var(--color-accent-subtle-border)]",
  success: "bg-[var(--color-success-subtle)] text-[var(--color-success)] border-transparent",
  warning: "bg-[var(--color-warning-subtle)] text-[var(--color-warning)] border-transparent",
  danger: "bg-[var(--color-danger-subtle)] text-[var(--color-danger)] border-transparent",
  info: "bg-[var(--color-info-subtle)] text-[var(--color-info)] border-transparent",
} as const;

export function Badge({
  tone = "neutral",
  className,
  children,
}: {
  tone?: keyof typeof TONES;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-[12px] font-medium leading-none",
        TONES[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
