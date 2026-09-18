"use client";

import { Briefcase } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { JobCardSkeleton } from "@/components/ui/skeleton";
import { EmptyState, ErrorState } from "@/components/ui/state-views";
import { ApplicationRow } from "@/components/saved/application-row";
import { STATUS_BADGE_TONE, STATUS_LABELS, STATUS_ORDER } from "@/components/saved/status-meta";
import type { ApplicationOut, ApplicationStatus } from "@/lib/types";

export function ApplicationsList({
  applications,
  isLoading,
  error,
  onRetry,
  onStatusChange,
  onNotesSave,
}: {
  applications: ApplicationOut[] | undefined;
  isLoading: boolean;
  error: unknown;
  onRetry: () => void;
  onStatusChange: (jobId: string, status: ApplicationStatus, notes: string | null) => Promise<void>;
  onNotesSave: (jobId: string, status: ApplicationStatus, notes: string) => Promise<void>;
}) {
  if (error) {
    return <ErrorState description="We couldn't load your applications. Please try again." onRetry={onRetry} />;
  }

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2">
        <JobCardSkeleton />
        <JobCardSkeleton />
      </div>
    );
  }

  if (!applications || applications.length === 0) {
    return (
      <EmptyState
        icon={Briefcase}
        title="No applications tracked yet"
        description="Applying starts from a saved job. Save a job, then mark it applied from the Saved tab to start tracking its progress here."
      />
    );
  }

  const groups = STATUS_ORDER.map((status) => ({
    status,
    items: applications.filter((a) => a.status === status),
  })).filter((group) => group.items.length > 0);

  return (
    <div className="space-y-10">
      {groups.map((group) => (
        <section key={group.status}>
          <div className="mb-4 flex items-center gap-2.5">
            <h2 className="text-[15px] font-semibold text-[var(--color-text-primary)]">
              {STATUS_LABELS[group.status]}
            </h2>
            <Badge tone={STATUS_BADGE_TONE[group.status]}>{group.items.length}</Badge>
          </div>
          <div className="space-y-5">
            {group.items.map((app) => (
              <ApplicationRow
                key={app.id}
                application={app}
                onStatusChange={onStatusChange}
                onNotesSave={onNotesSave}
                className="max-w-2xl"
              />
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
