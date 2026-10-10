import { cn } from "@/lib/utils";

export const BUTTON_VARIANTS = {
  primary:
    "bg-[var(--color-text-primary)] text-[var(--color-bg)] shadow-[var(--shadow-sm)] hover:opacity-90 hover:shadow-[var(--shadow-md)] disabled:opacity-40",
  accent:
    "bg-[var(--color-accent)] text-[var(--color-text-on-accent)] shadow-[inset_0_1px_0_rgb(255_255_255/0.18),0_8px_20px_-8px_var(--color-accent)] hover:bg-[var(--color-accent-hover)] hover:shadow-[inset_0_1px_0_rgb(255_255_255/0.18),0_12px_28px_-8px_var(--color-accent)] disabled:opacity-40 disabled:shadow-none",
  secondary:
    "bg-[var(--color-bg-subtle)] text-[var(--color-text-primary)] border border-[var(--color-border)] hover:border-[var(--color-border-strong)] disabled:opacity-40",
  outline:
    "bg-[var(--color-surface)]/60 text-[var(--color-text-primary)] border border-[var(--color-border-strong)] backdrop-blur-sm hover:bg-[var(--color-bg-subtle)] disabled:opacity-40",
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
    "inline-flex items-center justify-center rounded-[var(--radius-sm)] font-medium cursor-pointer select-none",
    "transition-[color,background-color,border-color,box-shadow,opacity,transform] duration-200 ease-out",
    "active:scale-[0.98] disabled:cursor-not-allowed disabled:active:scale-100",
    BUTTON_VARIANTS[variant],
    BUTTON_SIZES[size],
    className
  );
}
