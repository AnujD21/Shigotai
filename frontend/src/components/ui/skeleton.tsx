import { cn } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  // A light sweep reads as "loading" more clearly than a pulse; the
  // reduced-motion rule in globals.css freezes it for users who opt out.
  return (
    <div
      className={cn("relative overflow-hidden rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)]", className)}
      aria-hidden
    >
      <div className="absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent via-[var(--color-surface)]/70 to-transparent" />
    </div>
  );
}

export function JobCardSkeleton() {
  return (
    <div className="rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-2.5">
          <Skeleton className="h-4 w-1/3" />
          <Skeleton className="h-5 w-2/3" />
          <Skeleton className="h-3.5 w-1/2" />
        </div>
        <Skeleton className="h-8 w-20 shrink-0" />
      </div>
      <div className="mt-4 flex gap-2">
        <Skeleton className="h-6 w-16" />
        <Skeleton className="h-6 w-20" />
        <Skeleton className="h-6 w-14" />
      </div>
    </div>
  );
}
