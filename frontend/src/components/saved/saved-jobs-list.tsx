"use client";

import { Bookmark } from "lucide-react";
import { JobCard } from "@/components/jobs/job-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { JobCardSkeleton } from "@/components/ui/skeleton";
import { EmptyState, ErrorState } from "@/components/ui/state-views";
import { LinkButton } from "@/components/ui/link-button";
import { STATUS_BADGE_TONE, STATUS_LABELS } from "@/components/saved/status-meta";
import type { ApplicationStatus, SavedJobOut } from "@/lib/types";

export function SavedJobsList({
  savedJobs,
  isLoading,
  error,
  onRetry,
  onUnsave,
  onMarkApplied,
  pendingJobIds,
}: {
  savedJobs: SavedJobOut[] | undefined;
  isLoading: boolean;
  error: unknown;
  onRetry: () => void;
  onUnsave: (saved: SavedJobOut) => void;
  onMarkApplied: (saved: SavedJobOut) => void;
  pendingJobIds: Set<string>;
}) {
  if (error) {
    return <ErrorState description="We couldn't load your saved jobs. Please try again." onRetry={onRetry} />;
  }

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2">
        <JobCardSkeleton />
        <JobCardSkeleton />
        <JobCardSkeleton />
        <JobCardSkeleton />
      </div>
    );
  }

  if (!savedJobs || savedJobs.length === 0) {
    return (
      <EmptyState
        icon={Bookmark}
        title="You haven't saved any jobs yet"
        description="Save jobs you're interested in to keep track of them here."
        action={
          <LinkButton href="/jobs" variant="accent" size="sm">
            Browse jobs
          </LinkButton>
        }
      />
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {savedJobs.map((saved) => {
        const status = saved.application_status as ApplicationStatus | null;
        const hasApplied = !!status && status !== "SAVED";
        const isPending = pendingJobIds.has(saved.job.id);
        return (
          <div key={saved.id} className="flex flex-col gap-3">
            <JobCard job={saved.job} saved onToggleSave={() => onUnsave(saved)} />
            <div className="flex items-center justify-between gap-3 px-1">
              {status ? (
                <Badge tone={STATUS_BADGE_TONE[status]}>{STATUS_LABELS[status]}</Badge>
              ) : (
                <span className="text-[12.5px] text-[var(--color-text-tertiary)]">Not applied yet</span>
              )}
              {!hasApplied && (
                <Button variant="outline" size="sm" isLoading={isPending} onClick={() => onMarkApplied(saved)}>
                  Mark as applied
                </Button>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
