import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { CalendarClock, ExternalLink, MapPin } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { JobStatusIndicator } from "@/components/ui/status-indicator";
import { buttonClasses } from "@/components/ui/button-styles";
import { JobSaveButton } from "@/components/jobs/job-save-button";
import { JobMatchPanel } from "@/components/jobs/job-match-panel";
import { formatSalary, titleCase } from "@/lib/utils";
import type { JobDetail } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function getJob(id: string): Promise<JobDetail | null> {
  const res = await fetch(`${API_BASE_URL}/jobs/${id}`, { cache: "no-store" });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to load job.");
  return res.json();
}

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const job = await getJob(id);
  if (!job) return { title: "Job not found — Shigotai" };
  return {
    title: `${job.title} at ${job.company.name} — Shigotai`,
    description: `${job.title} at ${job.company.name}, ${job.location ?? "Japan"}. ${titleCase(job.employment_type)} · ${titleCase(job.work_mode)}.`,
  };
}

export default async function JobDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const job = await getJob(id);
  if (!job) notFound();

  const salary = formatSalary(job.salary_min, job.salary_max, job.salary_currency);

  return (
    <div className="mx-auto max-w-4xl px-5 py-10 md:px-8">
      <div className="mb-6">
        <Link
          href="/jobs"
          className="text-[13px] font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-accent)]"
        >
          ← Back to Discover Jobs
        </Link>
      </div>

      <div className="rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-6 md:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <Link
                href={`/companies/${job.company.slug}`}
                className="text-[14px] font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-accent)]"
              >
                {job.company.name}
              </Link>
              {job.is_demo_data && <Badge tone="neutral">Demo data -- fictional job for illustration</Badge>}
            </div>
            <h1 className="mt-1 text-[26px] font-semibold tracking-tight text-[var(--color-text-primary)] md:text-[30px]">
              {job.title}
            </h1>
            <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-[13.5px] text-[var(--color-text-tertiary)]">
              {job.location && (
                <span className="flex items-center gap-1">
                  <MapPin className="size-3.5" aria-hidden /> {job.location}
                </span>
              )}
              <span>{titleCase(job.employment_type)}</span>
              <span>{titleCase(job.work_mode)}</span>
              {salary && <span>{salary}</span>}
              {job.application_deadline && (
                <span className="flex items-center gap-1">
                  <CalendarClock className="size-3.5" aria-hidden />
                  Deadline {new Date(job.application_deadline).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                  })}
                </span>
              )}
            </div>
            <div className="mt-3">
              <JobStatusIndicator status={job.status} lastVerifiedAt={job.last_verified_at} />
            </div>
          </div>
          <JobSaveButton jobId={job.id} />
        </div>

        <div className="mt-6 flex flex-col gap-3 border-t border-[var(--color-border)] pt-6 sm:flex-row">
          <a
            href={job.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className={buttonClasses("accent", "md")}
          >
            Apply on Official Source
            <ExternalLink className="size-4" aria-hidden />
          </a>
        </div>
      </div>

      <div className="mt-8">
        <JobMatchPanel jobId={job.id} />
      </div>

      <div className="mt-8 rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-6 md:p-8">
        <h2 className="text-[16px] font-semibold text-[var(--color-text-primary)]">Job description</h2>
        {job.description_language && job.description_language.toLowerCase() !== "en" && (
          <p className="mt-1 text-[12.5px] text-[var(--color-text-tertiary)]">
            Original language: {job.description_language.toUpperCase()} -- shown exactly as posted, unedited.
          </p>
        )}
        <p className="mt-4 whitespace-pre-line text-[14.5px] leading-relaxed text-[var(--color-text-secondary)]">
          {job.original_description}
        </p>
      </div>
    </div>
  );
}
