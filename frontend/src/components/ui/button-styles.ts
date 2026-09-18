import { cn } from "@/lib/utils";

export const BUTTON_VARIANTS = {
  primary: "bg-[var(--color-text-primary)] text-[var(--color-bg)] hover:opacity-90 disabled:opacity-40",
  accent:
    "bg-[var(--color-accent)] text-[var(--color-text-on-accent)] hover:bg-[var(--color-accent-hover)] disabled:opacity-40",
  secondary:
    "bg-[var(--color-bg-subtle)] text-[var(--color-text-primary)] border border-[var(--color-border)] hover:border-[var(--color-border-strong)] disabled:opacity-40",
  outline:
    "bg-transparent text-[var(--color-text-primary)] border border-[var(--color-border-strong)] hover:bg-[var(--color-bg-subtle)] disabled:opacity-40",
  ghost:
    "bg-transparent text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-subtle)] disabled:opacity-40",
  destructive:
    "bg-transparent text-[var(--color-danger)] border border-[var(--color-danger)]/30 hover:bg-[var(--color-danger-subtle)] disabled:opacity-40",
} as const;

export const BUTTON_SIZES = {
  sm: "h-8 px-3 text-[13px] gap-1.5",
  md: "h-10 px-4 text-sm gap-2",
  lg: "h-12 px-6 text-[15px] gap-2",
} as const;

export function buttonClasses(
  variant: keyof typeof BUTTON_VARIANTS = "primary",
  size: keyof typeof BUTTON_SIZES = "md",
  className?: string
) {
  return cn(
    "inline-flex items-center justify-center rounded-[var(--radius-sm)] font-medium transition-colors cursor-pointer disabled:cursor-not-allowed",
    BUTTON_VARIANTS[variant],
    BUTTON_SIZES[size],
    className
  );
}
