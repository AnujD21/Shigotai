"use client";

import useSWR from "swr";
import Link from "next/link";
import { Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LinkButton } from "@/components/ui/link-button";
import { ErrorState } from "@/components/ui/state-views";
import { MatchStrengthBadge } from "@/components/jobs/match-strength-badge";
import { RequirementBreakdown } from "@/components/jobs/requirement-breakdown";
import { useAuth } from "@/lib/auth-context";
import { ApiError } from "@/lib/api";
import type { MatchOut } from "@/lib/types";

export function JobMatchPanel({ jobId }: { jobId: string }) {
  const { user, isLoading: authLoading } = useAuth();

  if (authLoading) {
    return (
      <Card>
        <CardContent className="pt-5">
          <div className="h-24 animate-pulse rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)]" />
        </CardContent>
      </Card>
    );
  }

  if (!user) {
    return (
      <Card>
        <CardContent className="flex flex-col items-start gap-3 pt-5">
          <div className="flex size-9 items-center justify-center rounded-full bg-[var(--color-accent-subtle)]">
            <Sparkles className="size-4 text-[var(--color-accent)]" aria-hidden />
          </div>
          <div>
            <p className="text-[15px] font-medium text-[var(--color-text-primary)]">See how well you match this role</p>
            <p className="mt-1 text-[13.5px] text-[var(--color-text-secondary)]">
              Log in to get a transparent, requirement-by-requirement breakdown of your fit for this job -- never a
              mystery score.
            </p>
          </div>
          <LinkButton href="/login" variant="accent" size="sm">
            Log in to see how well you match
          </LinkButton>
        </CardContent>
      </Card>
    );
  }

  return <AuthedMatchPanel jobId={jobId} />;
}

function AuthedMatchPanel({ jobId }: { jobId: string }) {
  const { data, error, isLoading, mutate } = useSWR<MatchOut>(`/matches/by-job/${jobId}`, {
    shouldRetryOnError: (err) => !(err instanceof ApiError && err.status === 404),
  });

  const notMatchedYet = error instanceof ApiError && error.status === 404;

  if (isLoading) {
    return (
      <Card>
        <CardContent className="space-y-3 pt-5">
          <div className="h-4 w-1/3 animate-pulse rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)]" />
          <div className="h-20 w-full animate-pulse rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)]" />
        </CardContent>
      </Card>
    );
  }

  if (notMatchedYet) {
    return (
      <Card>
        <CardContent className="pt-5">
          <p className="text-[14px] text-[var(--color-text-secondary)]">
            We haven&apos;t matched this job to your profile yet -- try refreshing your matches from the{" "}
            <Link href="/dashboard" className="font-medium text-[var(--color-accent)] hover:underline">
              dashboard
            </Link>
            .
          </p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return <ErrorState description="We couldn't load your match details for this job." onRetry={() => mutate()} />;
  }

  if (!data) return null;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between gap-4">
        <CardTitle as="h2">Why you match</CardTitle>
        <MatchStrengthBadge strength={data.match_strength} />
      </CardHeader>
      <CardContent>
        {data.ai_explanation && (
          <div className="mb-5 rounded-[var(--radius-md)] border border-[var(--color-accent-subtle-border)] bg-[var(--color-accent-subtle)] p-4">
            <p className="text-[13.5px] leading-relaxed text-[var(--color-text-primary)]">{data.ai_explanation}</p>
          </div>
        )}
        <RequirementBreakdown items={data.requirement_breakdown} />
      </CardContent>
    </Card>
  );
}
