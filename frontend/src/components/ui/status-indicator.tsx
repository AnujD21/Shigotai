import { AlertTriangle, CheckCircle2, CircleDashed, XCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { formatRelativeTime } from "@/lib/utils";
import type { JobStatus, RequirementState } from "@/lib/types";

export function JobStatusIndicator({ status, lastVerifiedAt }: { status: JobStatus; lastVerifiedAt: string | null }) {
  if (status === "ACTIVE") {
    return (
      <div className="flex items-center gap-1.5 text-[13px]">
        <span className="relative flex size-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[var(--color-success)] opacity-50" />
          <span className="relative inline-flex size-2 rounded-full bg-[var(--color-success)]" />
        </span>
        <span className="font-medium text-[var(--color-success)]">Verified active</span>
        <span className="text-[var(--color-text-tertiary)]">&middot; {formatRelativeTime(lastVerifiedAt)}</span>
      </div>
    );
  }
  if (status === "STALE") {
    return (
      <div className="flex items-center gap-1.5 text-[13px] text-[var(--color-warning)]">
        <AlertTriangle className="size-3.5" aria-hidden />
        <span className="font-medium">Possibly stale</span>
        <span className="text-[var(--color-text-tertiary)]">&middot; last checked {formatRelativeTime(lastVerifiedAt)}</span>
      </div>
    );
  }
  if (status === "CLOSED") {
    return (
      <div className="flex items-center gap-1.5 text-[13px] text-[var(--color-text-tertiary)]">
        <XCircle className="size-3.5" aria-hidden />
        <span className="font-medium">No longer listed</span>
      </div>
    );
  }
  return (
    <div className="flex items-center gap-1.5 text-[13px] text-[var(--color-text-tertiary)]">
      <CircleDashed className="size-3.5" aria-hidden />
      <span>Status unknown</span>
    </div>
  );
}

const STATE_CONFIG: Record<RequirementState, { icon: typeof CheckCircle2; className: string }> = {
  MATCH: { icon: CheckCircle2, className: "text-[var(--color-success)]" },
  PARTIAL: { icon: AlertTriangle, className: "text-[var(--color-warning)]" },
  MISSING: { icon: XCircle, className: "text-[var(--color-text-tertiary)]" },
  UNKNOWN: { icon: CircleDashed, className: "text-[var(--color-text-tertiary)]" },
};

export function RequirementIcon({ state, className }: { state: RequirementState; className?: string }) {
  const config = STATE_CONFIG[state];
  const Icon = config.icon;
  return <Icon className={cn("size-4 shrink-0", config.className, className)} aria-hidden />;
}
