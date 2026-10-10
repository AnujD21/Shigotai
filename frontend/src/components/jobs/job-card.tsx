"use client";

import Link from "next/link";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ArrowUpRight, Bookmark, BookmarkCheck, MapPin } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { JobStatusIndicator } from "@/components/ui/status-indicator";
import { MatchStrengthBadge } from "@/components/jobs/match-strength-badge";
import { trackSpotlight } from "@/components/motion/spotlight-card";
import { cn, formatRelativeTime, formatSalary, titleCase } from "@/lib/utils";
import type { JobCard as JobCardType } from "@/lib/types";

const MAX_STAGGERED = 8;

export function JobCard({
  job,
  saved,
  onToggleSave,
  className,
  index = 0,
}: {
  job: JobCardType;
  saved?: boolean;
  onToggleSave?: (job: JobCardType) => void;
  className?: string;
  /** Position in a list; staggers the entrance (capped so long lists don't lag). */
  index?: number;
}) {
  const reduce = useReducedMotion();
  const salary = formatSalary(job.salary_min, job.salary_max, job.salary_currency);
  const japanese = job.requirement?.jlpt_requirement
    ? `JLPT ${job.requirement.jlpt_requirement}+`
    : job.requirement?.japanese_requirement_raw
      ? "Business Japanese"
      : null;

  return (
    <motion.article
      initial={{ opacity: 0, y: reduce ? 0 : 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={reduce ? undefined : { y: -3, transition: { type: "spring", stiffness: 400, damping: 26 } }}
      transition={{
        opacity: { duration: 0.35, delay: Math.min(index, MAX_STAGGERED) * 0.045 },
        y: { type: "spring", stiffness: 320, damping: 26, delay: Math.min(index, MAX_STAGGERED) * 0.045 },
      }}
      onPointerMove={trackSpotlight}
      className={cn(
        "spotlight group relative flex flex-col rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-5 shadow-[var(--shadow-xs)] transition-shadow duration-300 hover:shadow-[var(--shadow-md)]",
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
            <h3 className="text-[16px] font-semibold leading-snug text-[var(--color-text-primary)] transition-colors group-hover:text-[var(--color-accent)]">
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
            {job.work_mode !== "UNKNOWN" && <span>{titleCase(job.work_mode)}</span>}
            <span>{titleCase(job.employment_type)}</span>
            {salary && <span className="tabular-nums">{salary}</span>}
          </div>
        </div>
      </div>

      <div className="mb-4 mt-3.5 flex flex-wrap items-center gap-1.5">
        <MatchStrengthBadge strength={job.match_strength} />
        {japanese && <Badge tone="info">{japanese}</Badge>}
        {job.requirement?.visa_sponsorship === "YES" && <Badge tone="accent">Visa sponsorship</Badge>}
        {job.requirement?.new_graduate_allowed && <Badge tone="neutral">New graduates welcome</Badge>}
        {job.requirement?.required_skills.slice(0, 3).map((skill) => (
          <Badge key={skill}>{skill}</Badge>
        ))}
      </div>

      <div className="mt-auto flex items-center justify-between border-t border-[var(--color-border)] pt-3.5">
        <JobStatusIndicator status={job.status} lastVerifiedAt={job.last_verified_at} />
        <div className="flex items-center gap-1">
          {onToggleSave && (
            <motion.button
              type="button"
              onClick={() => onToggleSave(job)}
              whileTap={{ scale: 0.82 }}
              aria-label={saved ? "Remove from saved jobs" : "Save job"}
              aria-pressed={saved}
              className="flex size-9 items-center justify-center rounded-[var(--radius-sm)] text-[var(--color-text-tertiary)] transition-colors hover:bg-[var(--color-bg-subtle)] hover:text-[var(--color-text-primary)]"
            >
              <AnimatePresence mode="wait" initial={false}>
                <motion.span
                  key={saved ? "saved" : "unsaved"}
                  initial={{ scale: 0.4, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.4, opacity: 0 }}
                  transition={{ type: "spring", stiffness: 520, damping: 22 }}
                  className="flex"
                >
                  {saved ? (
                    <BookmarkCheck className="size-4 text-[var(--color-accent)]" aria-hidden />
                  ) : (
                    <Bookmark className="size-4" aria-hidden />
                  )}
                </motion.span>
              </AnimatePresence>
            </motion.button>
          )}
          <Link
            href={`/jobs/${job.id}`}
            className="inline-flex items-center gap-0.5 rounded-[var(--radius-sm)] px-1.5 py-1 text-[13px] font-medium text-[var(--color-text-primary)] transition-colors hover:text-[var(--color-accent)]"
          >
            View job
            <ArrowUpRight
              className="size-3.5 transition-transform duration-200 group-hover:-translate-y-px group-hover:translate-x-px"
              aria-hidden
            />
          </Link>
        </div>
      </div>

      <p className="mt-2.5 text-[11.5px] text-[var(--color-text-tertiary)]">
        First seen {formatRelativeTime(job.first_seen_at)}
      </p>
    </motion.article>
  );
}
