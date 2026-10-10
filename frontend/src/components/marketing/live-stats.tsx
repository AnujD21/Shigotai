"use client";

import useSWR from "swr";
import { motion } from "framer-motion";
import { CountUp } from "@/components/motion/count-up";
import type { CompanySummary, JobListResponse } from "@/lib/types";

/**
 * Real numbers from the API ("312 open roles · 34 companies"), so the hero
 * proves the data is live. Renders nothing until both requests succeed --
 * a marketing page should never show an error state for a nice-to-have.
 */
export function LiveStats() {
  const { data: jobs } = useSWR<JobListResponse>("/jobs?page_size=1&only_verified_active=true");
  const { data: companies } = useSWR<CompanySummary[]>("/companies");

  const ready = jobs && companies && jobs.total > 0;

  return (
    <div className="h-6">
      {ready && (
        <motion.p
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center gap-2 text-[13px] text-[var(--color-text-secondary)]"
        >
          <span className="relative flex size-2" aria-hidden>
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[var(--color-success)] opacity-60" />
            <span className="relative inline-flex size-2 rounded-full bg-[var(--color-success)]" />
          </span>
          <span>
            <CountUp value={jobs.total} className="font-semibold tabular-nums text-[var(--color-text-primary)]" /> open
            roles in Japan from{" "}
            <CountUp value={companies.length} className="font-semibold tabular-nums text-[var(--color-text-primary)]" />{" "}
            companies, verified against their career boards
          </span>
        </motion.p>
      )}
    </div>
  );
}
