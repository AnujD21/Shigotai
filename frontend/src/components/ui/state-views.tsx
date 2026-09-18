import type { LucideIcon } from "lucide-react";
import { AlertCircle, InboxIcon } from "lucide-react";
import { Button } from "@/components/ui/button";

export function EmptyState({
  icon: Icon = InboxIcon,
  title,
  description,
  action,
}: {
  icon?: LucideIcon;
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-[var(--radius-lg)] border border-dashed border-[var(--color-border-strong)] px-6 py-16 text-center">
      <div className="mb-4 flex size-11 items-center justify-center rounded-full bg-[var(--color-bg-subtle)]">
        <Icon className="size-5 text-[var(--color-text-tertiary)]" aria-hidden />
      </div>
      <p className="text-[15px] font-medium text-[var(--color-text-primary)]">{title}</p>
      {description && <p className="mt-1.5 max-w-sm text-[13.5px] text-[var(--color-text-secondary)]">{description}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

export function ErrorState({
  title = "Something went wrong",
  description = "We couldn't load this. Please try again.",
  onRetry,
}: {
  title?: string;
  description?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-danger-subtle)]/40 px-6 py-16 text-center">
      <div className="mb-4 flex size-11 items-center justify-center rounded-full bg-[var(--color-danger-subtle)]">
        <AlertCircle className="size-5 text-[var(--color-danger)]" aria-hidden />
      </div>
      <p className="text-[15px] font-medium text-[var(--color-text-primary)]">{title}</p>
      <p className="mt-1.5 max-w-sm text-[13.5px] text-[var(--color-text-secondary)]">{description}</p>
      {onRetry && (
        <Button variant="outline" size="sm" className="mt-5" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  );
}
