"use client";

import { useState } from "react";
import useSWR from "swr";
import { toast } from "sonner";
import { PageHeader } from "@/components/ui/page-header";
import { Tabs } from "@/components/ui/tabs";
import { SavedJobsList } from "@/components/saved/saved-jobs-list";
import { ApplicationsList } from "@/components/saved/applications-list";
import { STATUS_LABELS } from "@/components/saved/status-meta";
import { api, ApiError } from "@/lib/api";
import type { ApplicationOut, ApplicationStatus, SavedJobOut } from "@/lib/types";

type TabValue = "saved" | "applications";

export default function SavedJobsPage() {
  const [tab, setTab] = useState<TabValue>("saved");
  const [pendingJobIds, setPendingJobIds] = useState<Set<string>>(new Set());

  const {
    data: savedJobs,
    error: savedError,
    isLoading: savedLoading,
    mutate: mutateSaved,
  } = useSWR<SavedJobOut[]>("/saved-jobs");

  const {
    data: applications,
    error: applicationsError,
    isLoading: applicationsLoading,
    mutate: mutateApplications,
  } = useSWR<ApplicationOut[]>("/applications");

  const activeApplicationsCount = applications
    ? applications.filter((a) => a.status !== "ARCHIVED").length
    : undefined;

  function setPending(jobId: string, pending: boolean) {
    setPendingJobIds((prev) => {
      const next = new Set(prev);
      if (pending) next.add(jobId);
      else next.delete(jobId);
      return next;
    });
  }

  async function handleUnsave(saved: SavedJobOut) {
    const jobId = saved.job.id;
    mutateSaved((current) => current?.filter((s) => s.id !== saved.id), false);
    try {
      await api.delete(`/jobs/${jobId}/save`);
      toast.success("Removed from saved jobs");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't remove this job. Please try again.");
      mutateSaved();
    }
  }

  async function handleMarkApplied(saved: SavedJobOut) {
    const jobId = saved.job.id;
    setPending(jobId, true);
    try {
      const updated = await api.put<ApplicationOut>(`/applications/${jobId}`, { status: "APPLIED" });
      mutateSaved(
        (current) => current?.map((s) => (s.id === saved.id ? { ...s, application_status: updated.status } : s)),
        false
      );
      mutateApplications((current) => {
        if (!current) return current;
        const exists = current.some((a) => a.id === updated.id);
        return exists ? current.map((a) => (a.id === updated.id ? updated : a)) : [updated, ...current];
      }, false);
      toast.success("Marked as applied", {
        description: "Track its progress from the Applications tab.",
        action: { label: "View", onClick: () => setTab("applications") },
      });
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't update this application. Please try again.");
    } finally {
      setPending(jobId, false);
    }
  }

  async function handleStatusChange(jobId: string, status: ApplicationStatus, notes: string | null) {
    try {
      const updated = await api.put<ApplicationOut>(`/applications/${jobId}`, {
        status,
        notes: notes ?? undefined,
      });
      mutateApplications((current) => current?.map((a) => (a.id === updated.id ? updated : a)), false);
      mutateSaved(
        (current) => current?.map((s) => (s.job.id === jobId ? { ...s, application_status: updated.status } : s)),
        false
      );
      toast.success(`Status updated to "${STATUS_LABELS[status]}"`);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't update status. Please try again.");
      mutateApplications();
      throw err;
    }
  }

  async function handleNotesSave(jobId: string, status: ApplicationStatus, notes: string) {
    try {
      const updated = await api.put<ApplicationOut>(`/applications/${jobId}`, { status, notes });
      mutateApplications((current) => current?.map((a) => (a.id === updated.id ? updated : a)), false);
      toast.success("Note saved");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't save note. Please try again.");
      throw err;
    }
  }

  return (
    <>
      <PageHeader
        title="Saved jobs"
        description="Keep track of roles you're interested in and follow your application pipeline."
      />

      <h2 className="sr-only">Saved jobs and applications</h2>
      <Tabs
        tabs={[
          { value: "saved", label: "Saved", count: savedJobs?.length },
          { value: "applications", label: "Applications", count: activeApplicationsCount },
        ]}
        active={tab}
        onChange={(v) => setTab(v as TabValue)}
        className="mb-6"
      />

      {tab === "saved" && (
        <SavedJobsList
          savedJobs={savedJobs}
          isLoading={savedLoading}
          error={savedError}
          onRetry={() => mutateSaved()}
          onUnsave={handleUnsave}
          onMarkApplied={handleMarkApplied}
          pendingJobIds={pendingJobIds}
        />
      )}

      {tab === "applications" && (
        <ApplicationsList
          applications={applications}
          isLoading={applicationsLoading}
          error={applicationsError}
          onRetry={() => mutateApplications()}
          onStatusChange={handleStatusChange}
          onNotesSave={handleNotesSave}
        />
      )}
    </>
  );
}
