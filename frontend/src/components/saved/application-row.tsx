"use client";

import { useState } from "react";
import { Save } from "lucide-react";
import { JobCard } from "@/components/jobs/job-card";
import { Button } from "@/components/ui/button";
import { Select, Textarea } from "@/components/ui/input";
import { cn, formatRelativeTime } from "@/lib/utils";
import { STATUS_LABELS, STATUS_ORDER } from "@/components/saved/status-meta";
import type { ApplicationOut, ApplicationStatus } from "@/lib/types";

export function ApplicationRow({
  application,
  onStatusChange,
  onNotesSave,
  className,
}: {
  application: ApplicationOut;
  onStatusChange: (jobId: string, status: ApplicationStatus, notes: string | null) => Promise<void>;
  onNotesSave: (jobId: string, status: ApplicationStatus, notes: string) => Promise<void>;
  className?: string;
}) {
  const [localStatus, setLocalStatus] = useState<ApplicationStatus>(application.status);
  const [statusPending, setStatusPending] = useState(false);
  // Tracks the last server status we've synced from, so we can tell a real
  // server-side change apart from our own optimistic edit while rendering.
  const [syncedStatus, setSyncedStatus] = useState(application.status);

  const [notes, setNotes] = useState(application.notes ?? "");
  const [dirty, setDirty] = useState(false);
  const [notesPending, setNotesPending] = useState(false);
  const [syncedNotes, setSyncedNotes] = useState(application.notes ?? "");

  // Keep local copies in sync with the server once no local edit is in flight,
  // without clobbering what the person is actively doing. Adjusting state
  // during render (rather than in an effect) avoids an extra commit.
  if (application.status !== syncedStatus) {
    setSyncedStatus(application.status);
    if (!statusPending) setLocalStatus(application.status);
  }

  const incomingNotes = application.notes ?? "";
  if (incomingNotes !== syncedNotes) {
    setSyncedNotes(incomingNotes);
    if (!dirty) setNotes(incomingNotes);
  }

  async function handleStatusChange(value: string) {
    const nextStatus = value as ApplicationStatus;
    const previous = localStatus;
    setLocalStatus(nextStatus);
    setStatusPending(true);
    try {
      await onStatusChange(application.job.id, nextStatus, application.notes);
    } catch {
      setLocalStatus(previous);
    } finally {
      setStatusPending(false);
    }
  }

  async function handleSaveNotes() {
    setNotesPending(true);
    try {
      await onNotesSave(application.job.id, application.status, notes);
      setDirty(false);
    } catch {
      // Error toast is already surfaced by the caller -- keep the text and the
      // "unsaved" indicator so nothing typed is lost and the person can retry.
    } finally {
      setNotesPending(false);
    }
  }

  return (
    <div className={cn("flex flex-col gap-3", className)}>
      <JobCard job={application.job} />

      <div className="flex flex-col gap-3 rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-bg-subtle)] p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[12.5px] text-[var(--color-text-tertiary)]">
          <span>Applied {formatRelativeTime(application.applied_at)}</span>
          <span>Updated {formatRelativeTime(application.status_updated_at)}</span>
        </div>
        <Select
          aria-label="Application status"
          value={localStatus}
          disabled={statusPending}
          onChange={(e) => handleStatusChange(e.target.value)}
          className="w-full sm:w-44"
        >
          {STATUS_ORDER.map((s) => (
            <option key={s} value={s}>
              {STATUS_LABELS[s]}
            </option>
          ))}
        </Select>
      </div>

      <div>
        <Textarea
          aria-label="Notes"
          value={notes}
          placeholder="Interview prep, contacts, follow-ups..."
          onChange={(e) => {
            setNotes(e.target.value);
            setDirty(true);
          }}
          className="min-h-[72px]"
        />
        <div className="mt-2 flex items-center justify-end gap-3">
          {dirty && <span className="text-[12px] text-[var(--color-text-tertiary)]">Unsaved changes</span>}
          <Button variant="outline" size="sm" onClick={handleSaveNotes} isLoading={notesPending} disabled={!dirty}>
            <Save className="size-3.5" aria-hidden />
            Save note
          </Button>
        </div>
      </div>
    </div>
  );
}
