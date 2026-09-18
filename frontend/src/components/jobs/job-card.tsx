"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Bookmark, BookmarkCheck, MapPin } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { JobStatusIndicator } from "@/components/ui/status-indicator";
import { MatchStrengthBadge } from "@/components/jobs/match-strength-badge";
import { cn, formatRelativeTime, formatSalary, titleCase } from "@/lib/utils";
import type { JobCard as JobCardType } from "@/lib/types";

export function JobCard({
  job,
  saved,
  onToggleSave,
  className,
}: {
  job: JobCardType;
  saved?: boolean;
  onToggleSave?: (job: JobCardType) => void;
  className?: string;
}) {
  const salary = formatSalary(job.salary_min, job.salary_max, job.salary_currency);
  const japanese = job.requirement?.jlpt_requirement
    ? `JLPT ${job.requirement.jlpt_requirement}+`
    : job.requirement?.japanese_requirement_raw
      ? "Business Japanese"
      : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={cn(
        "group relative rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-5 transition-shadow hover:shadow-[var(--shadow-md)]",
        job.is_demo_data && "ring-1 ring-[var(--color-accent-subtle-border)]",
        className
      )}
    >
      {job.is_demo_data && (
        <span className="absolute right-5 top-5 text-[10.5px] font-medium uppercase tracking-wide text-[var(--color-text-tertiary)]">
          Demo data
        </span>
      )}
      <div className="flex items-start justify-between gap-4 pr-16">
        <div className="min-w-0 flex-1">
          <p className="truncate text-[13px] font-medium text-[var(--color-text-secondary)]">{job.company.name}</p>
          <Link href={`/jobs/${job.id}`} className="mt-0.5 block">
            <h3 className="text-[16px] font-semibold text-[var(--color-text-primary)] hover:text-[var(--color-accent)] transition-colors">
              {job.title}
            </h3>
          </Link>
          <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-[13px] text-[var(--color-text-tertiary)]">
            {job.location && (
              <span className="flex items-center gap-1">
                <MapPin className="size-3.5" aria-hidden />
                {job.location}
              </span>
            )}
            <span>{titleCase(job.work_mode)}</span>
            <span>{titleCase(job.employment_type)}</span>
            {salary && <span>{salary}</span>}
          </div>
        </div>
      </div>

      <div className="mt-3.5 flex flex-wrap items-center gap-1.5">
        <MatchStrengthBadge strength={job.match_strength} />
        {japanese && <Badge tone="info">{japanese}</Badge>}
        {job.requirement?.visa_sponsorship === "YES" && <Badge tone="accent">Visa sponsorship</Badge>}
        {job.requirement?.new_graduate_allowed && <Badge tone="neutral">New graduates welcome</Badge>}
        {job.requirement?.required_skills.slice(0, 3).map((skill) => (
          <Badge key={skill}>{skill}</Badge>
        ))}
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-[var(--color-border)] pt-3.5">
        <JobStatusIndicator status={job.status} lastVerifiedAt={job.last_verified_at} />
        <div className="flex items-center gap-2">
          {onToggleSave && (
            <button
              type="button"
              onClick={() => onToggleSave(job)}
              aria-label={saved ? "Remove from saved jobs" : "Save job"}
              aria-pressed={saved}
              className="flex size-8 items-center justify-center rounded-[var(--radius-sm)] text-[var(--color-text-tertiary)] transition-colors hover:bg-[var(--color-bg-subtle)] hover:text-[var(--color-text-primary)]"
            >
              {saved ? (
                <BookmarkCheck className="size-4 text-[var(--color-accent)]" aria-hidden />
              ) : (
                <Bookmark className="size-4" aria-hidden />
              )}
            </button>
          )}
          <Link
            href={`/jobs/${job.id}`}
            className="text-[13px] font-medium text-[var(--color-text-primary)] underline-offset-4 hover:text-[var(--color-accent)] hover:underline"
          >
            View job
          </Link>
        </div>
      </div>

      <p className="mt-2.5 text-[11.5px] text-[var(--color-text-tertiary)]">
        First seen {formatRelativeTime(job.first_seen_at)}
      </p>
    </motion.div>
  );
}
