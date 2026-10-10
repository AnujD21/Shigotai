"use client";

import useSWR from "swr";
import { Marquee } from "@/components/motion/marquee";
import type { CompanySummary } from "@/lib/types";

const MIN_COMPANIES = 6;

/** Companies with open roles right now, straight from the API. */
export function CompanyMarquee() {
  const { data } = useSWR<CompanySummary[]>("/companies");
  if (!data || data.length < MIN_COMPANIES) return null;

  return (
    <section aria-labelledby="hiring-now" className="border-y border-[var(--color-border)] bg-[var(--color-surface)]/50 py-9">
      <p
        id="hiring-now"
        className="mb-6 text-center text-[12.5px] font-medium tracking-wide text-[var(--color-text-tertiary)]"
      >
        Hiring in Japan right now
      </p>
      <Marquee
        durationSeconds={Math.max(30, data.length * 2.5)}
        items={data.map((company) => (
          <span
            key={company.id}
            className="whitespace-nowrap font-display text-[19px] font-medium text-[var(--color-text-secondary)] transition-colors hover:text-[var(--color-text-primary)]"
          >
            {company.name}
          </span>
        ))}
      />
    </section>
  );
}
