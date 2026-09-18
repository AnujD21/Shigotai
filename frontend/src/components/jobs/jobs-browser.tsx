"use client";

import { useCallback, useMemo } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { ChevronLeft, ChevronRight, SearchX } from "lucide-react";
import useSWR from "swr";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { JobCardSkeleton } from "@/components/ui/skeleton";
import { EmptyState, ErrorState } from "@/components/ui/state-views";
import { JobCard } from "@/components/jobs/job-card";
import { JobFilters, DEFAULT_JOB_FILTERS, type JobFilterValues } from "@/components/jobs/job-filters";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { JobCard as JobCardType, JobListResponse, SavedJobOut } from "@/lib/types";

const PAGE_SIZE = 20;
const FILTER_KEYS = Object.keys(DEFAULT_JOB_FILTERS) as (keyof JobFilterValues)[];

function parseFilters(params: URLSearchParams): JobFilterValues {
  return {
    q: params.get("q") ?? "",
    location: params.get("location") ?? "",
    employment_type: params.get("employment_type") ?? "",
    work_mode: params.get("work_mode") ?? "",
    only_verified_active: params.get("only_verified_active") === "true",
    new_graduate: params.get("new_graduate") === "true",
    visa_sponsorship: params.get("visa_sponsorship") === "true",
    sort: params.get("sort") ?? DEFAULT_JOB_FILTERS.sort,
  };
}

export function JobsBrowser() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { user } = useAuth();

  const filters = useMemo(() => parseFilters(searchParams), [searchParams]);
  const page = Math.max(1, Number(searchParams.get("page") ?? "1") || 1);

  const applyParams = useCallback(
    (patch: Partial<JobFilterValues> & { page?: number }, opts: { resetPage?: boolean } = {}) => {
      const { resetPage = true } = opts;
      const merged: JobFilterValues = { ...filters, ...patch };
      const next = new URLSearchParams(searchParams.toString());

      FILTER_KEYS.forEach((key) => {
        const value = merged[key];
        if (value === DEFAULT_JOB_FILTERS[key] || value === "" || value === false) {
          next.delete(key);
        } else {
          next.set(key, String(value));
        }
      });

      if (patch.page) {
        next.set("page", String(patch.page));
      } else if (resetPage) {
        next.delete("page");
      }

      const qs = next.toString();
      router.replace(qs ? `${pathname}?${qs}` : pathname, { scroll: false });
    },
    [filters, pathname, router, searchParams]
  );

  const apiQuery = useMemo(() => {
    const params = new URLSearchParams();
    if (filters.q) params.set("q", filters.q);
    if (filters.location) params.set("location", filters.location);
    if (filters.employment_type) params.set("employment_type", filters.employment_type);
    if (filters.work_mode) params.set("work_mode", filters.work_mode);
    if (filters.only_verified_active) params.set("only_verified_active", "true");
    if (filters.new_graduate) params.set("new_graduate", "true");
    if (filters.visa_sponsorship) params.set("visa_sponsorship", "true");
    params.set("sort", filters.sort);
    params.set("page", String(page));
    params.set("page_size", String(PAGE_SIZE));
    return params.toString();
  }, [filters, page]);

  const { data, error, isLoading, mutate } = useSWR<JobListResponse>(`/jobs?${apiQuery}`);
  const { data: savedJobs, mutate: mutateSaved } = useSWR<SavedJobOut[]>(user ? "/saved-jobs" : null);
  const savedIds = useMemo(() => new Set((savedJobs ?? []).map((s) => s.job.id)), [savedJobs]);

  const hasActiveFilters = useMemo(
    () => FILTER_KEYS.some((key) => filters[key] !== DEFAULT_JOB_FILTERS[key]),
    [filters]
  );

  const clearFilters = useCallback(() => {
    router.replace(pathname, { scroll: false });
  }, [pathname, router]);

  const handleToggleSave = useCallback(
    async (job: JobCardType) => {
      if (!user) {
        toast("Log in to save jobs", {
          description: "Create a free account to keep track of jobs you're interested in.",
          action: { label: "Log in", onClick: () => router.push("/login") },
        });
        return;
      }
      const isSaved = savedIds.has(job.id);
      try {
        if (isSaved) {
          await api.delete(`/jobs/${job.id}/save`);
        } else {
          await api.post(`/jobs/${job.id}/save`);
        }
        mutateSaved();
      } catch (err) {
        toast.error(err instanceof ApiError ? err.message : "Couldn't update saved jobs. Please try again.");
      }
    },
    [user, savedIds, mutateSaved, router]
  );

  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;

  return (
    <div className="space-y-6">
      <JobFilters
        key={`${filters.q}|${filters.location}`}
        values={filters}
        onTextChange={(patch) => applyParams(patch)}
        onImmediateChange={(patch) => applyParams(patch)}
        onClear={clearFilters}
        hasActiveFilters={hasActiveFilters}
      />

      {error && (
        <ErrorState description="We couldn't load jobs right now. Please try again." onRetry={() => mutate()} />
      )}

      {!error && isLoading && (
        <div className="grid gap-4 md:grid-cols-2">
          {Array.from({ length: 6 }).map((_, i) => (
            <JobCardSkeleton key={i} />
          ))}
        </div>
      )}

      {!error && !isLoading && data && data.items.length === 0 && (
        <EmptyState
          icon={SearchX}
          title="No jobs match your filters"
          description="Try widening your search or clearing filters to see more roles."
          action={
            <Button variant="outline" size="sm" onClick={clearFilters}>
              Clear filters
            </Button>
          }
        />
      )}

      {!error && !isLoading && data && data.items.length > 0 && (
        <>
          <h2 className="text-[13px] font-normal text-[var(--color-text-tertiary)]">
            {data.total} job{data.total === 1 ? "" : "s"} found
          </h2>
          <div className="grid gap-4 md:grid-cols-2">
            {data.items.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                saved={user ? savedIds.has(job.id) : undefined}
                onToggleSave={handleToggleSave}
              />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-3 pt-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => applyParams({ page: page - 1 }, { resetPage: false })}
              >
                <ChevronLeft className="size-4" aria-hidden />
                Previous
              </Button>
              <span className="text-[13px] text-[var(--color-text-tertiary)]">
                Page {page} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => applyParams({ page: page + 1 }, { resetPage: false })}
              >
                Next
                <ChevronRight className="size-4" aria-hidden />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
