"use client";

import { useMemo, useState } from "react";
import useSWR from "swr";
import { Sparkles } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { Tabs } from "@/components/ui/tabs";
import { JobCardSkeleton } from "@/components/ui/skeleton";
import { EmptyState, ErrorState } from "@/components/ui/state-views";
import { LinkButton } from "@/components/ui/link-button";
import { JobCard } from "@/components/jobs/job-card";
import type { MatchOut } from "@/lib/types";

interface MatchListResponse {
  items: MatchOut[];
  total: number;
}

type TabValue = "ALL" | "PARTIAL_PLUS" | "STRONG";

function isStrong(m: MatchOut) {
  return m.match_strength === "STRONG_MATCH";
}

function isPartialPlus(m: MatchOut) {
  return m.match_strength === "STRONG_MATCH" || m.match_strength === "PARTIAL_MATCH";
}

export default function MatchesPage() {
  const [tab, setTab] = useState<TabValue>("ALL");
  const { data, error, isLoading, mutate } = useSWR<MatchListResponse>("/matches?limit=50");

  const filtered = useMemo(() => {
    if (!data) return [];
    if (tab === "STRONG") return data.items.filter(isStrong);
    if (tab === "PARTIAL_PLUS") return data.items.filter(isPartialPlus);
    return data.items;
  }, [data, tab]);

  const tabs = useMemo(
    () => [
      { value: "ALL", label: "All", count: data?.total },
      { value: "PARTIAL_PLUS", label: "Partial+", count: data?.items.filter(isPartialPlus).length },
      { value: "STRONG", label: "Strong", count: data?.items.filter(isStrong).length },
    ],
    [data]
  );

  return (
    <>
      <PageHeader title="My Matches" description="Everything Shigotai has found for you so far, ranked by overall fit." />
      <h2 className="sr-only">Your matched jobs</h2>

      {!error && !isLoading && data && data.items.length > 0 && (
        <Tabs tabs={tabs} active={tab} onChange={(v) => setTab(v as TabValue)} className="mb-6" />
      )}

      {error && (
        <ErrorState description="We couldn't load your matches. Please try again." onRetry={() => mutate()} />
      )}

      {!error && isLoading && (
        <div className="grid gap-4 md:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <JobCardSkeleton key={i} />
          ))}
        </div>
      )}

      {!error && !isLoading && data && data.items.length === 0 && (
        <EmptyState
          icon={Sparkles}
          title="No matches yet"
          description="Matches depend on your profile. Add your skills, experience and Japanese ability to start seeing jobs matched to you."
          action={
            <LinkButton href="/profile" variant="accent" size="sm">
              Complete your profile
            </LinkButton>
          }
        />
      )}

      {!error && !isLoading && data && data.items.length > 0 && filtered.length === 0 && (
        <EmptyState title="No matches in this category" description="Try a different filter to see more of your matches." />
      )}

      {!error && !isLoading && filtered.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {filtered.map((match) => (
            <div key={match.id} className="flex flex-col gap-2.5">
              <JobCard job={match.job} />
              {match.ai_explanation && (
                <p className="line-clamp-2 px-1 text-[13px] leading-relaxed text-[var(--color-text-secondary)]">
                  {match.ai_explanation}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </>
  );
}
