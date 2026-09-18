"use client";

import useSWR from "swr";
import {
  Bell,
  Briefcase,
  Building2,
  Info,
  Mail,
  Sparkles,
  TrendingUp,
  UserCog,
} from "lucide-react";
import Link from "next/link";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ProgressBar } from "@/components/ui/progress-bar";
import { Skeleton, JobCardSkeleton } from "@/components/ui/skeleton";
import { EmptyState, ErrorState } from "@/components/ui/state-views";
import { LinkButton } from "@/components/ui/link-button";
import { JobCard } from "@/components/jobs/job-card";
import { StatTile } from "@/components/dashboard/stat-tile";
import { BarList } from "@/components/dashboard/bar-list";
import { useAuth } from "@/lib/auth-context";
import { formatRelativeTime } from "@/lib/utils";
import type { DashboardSummary, NotificationOut, NotificationType } from "@/lib/types";

const ALERT_ICONS: Record<NotificationType, typeof Bell> = {
  NEW_MATCH: Sparkles,
  JOB_BECAME_MATCH: TrendingUp,
  JOB_STATUS_CHANGED: Info,
  DIGEST: Mail,
  SYSTEM: Bell,
};

export default function DashboardPage() {
  const { user } = useAuth();
  const { data, error, isLoading, mutate } = useSWR<DashboardSummary>("/dashboard/summary");

  const firstName = user?.full_name?.split(" ")[0];

  return (
    <>
      <PageHeader
        title="Dashboard"
        description={
          firstName
            ? `Welcome back, ${firstName}. Here's what's new in your job search.`
            : "Here's what's new in your job search."
        }
      />

      {error && <ErrorState description="We couldn't load your dashboard. Please try again." onRetry={() => mutate()} />}

      {!error && isLoading && <DashboardSkeleton />}

      {!error && !isLoading && data && <DashboardContent data={data} />}
    </>
  );
}

function DashboardContent({ data }: { data: DashboardSummary }) {
  const isComplete = data.profile_completeness >= 100;

  const statTiles = [
    { label: "New jobs today", value: data.new_jobs_today, icon: Briefcase },
    { label: "Highly relevant matches", value: data.highly_relevant_count, icon: Sparkles },
    { label: "Saved jobs", value: data.saved_jobs_count, icon: TrendingUp },
    { label: "Applications", value: data.applications_count, icon: Mail },
    { label: "Companies hiring", value: data.companies_hiring_count, icon: Building2 },
  ];

  return (
    <div className="space-y-10">
      {/* Profile completeness */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4">
          <CardTitle as="h2">Profile completeness</CardTitle>
          <span className="text-[15px] font-semibold text-[var(--color-text-primary)]">
            {data.profile_completeness}%
          </span>
        </CardHeader>
        <CardContent>
          <ProgressBar value={data.profile_completeness} />
          {isComplete ? (
            <p className="mt-4 flex items-center gap-2 text-[13.5px] text-[var(--color-text-secondary)]">
              <Sparkles className="size-4 text-[var(--color-accent)]" aria-hidden />
              Your profile is complete -- Shigotai has everything it needs to match you well.
            </p>
          ) : data.completeness_suggestions.length > 0 ? (
            <div className="mt-4">
              <p className="text-[13px] font-medium text-[var(--color-text-primary)]">To improve your matches:</p>
              <ul className="mt-2 space-y-1.5">
                {data.completeness_suggestions.map((suggestion) => (
                  <li key={suggestion} className="flex items-start gap-2 text-[13.5px] text-[var(--color-text-secondary)]">
                    <span className="mt-2 size-1 shrink-0 rounded-full bg-[var(--color-text-tertiary)]" aria-hidden />
                    {suggestion}
                  </li>
                ))}
              </ul>
              <LinkButton href="/profile" variant="outline" size="sm" className="mt-4">
                <UserCog className="size-3.5" aria-hidden />
                Complete your profile
              </LinkButton>
            </div>
          ) : null}
        </CardContent>
      </Card>

      {/* Stat tiles */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
        {statTiles.map((tile) => (
          <StatTile key={tile.label} label={tile.label} value={tile.value} icon={tile.icon} />
        ))}
      </div>

      {/* Top matches */}
      <section>
        <h2 className="text-[17px] font-semibold tracking-tight text-[var(--color-text-primary)]">
          Jobs matching you
        </h2>
        {data.top_matches.length === 0 ? (
          <div className="mt-4">
            <EmptyState
              icon={Sparkles}
              title="No matches yet"
              description="Complete your profile to start seeing matches. The more detail Shigotai has, the sharper your results."
              action={
                <LinkButton href="/profile" variant="accent" size="sm">
                  Complete your profile to start seeing matches
                </LinkButton>
              }
            />
          </div>
        ) : (
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {data.top_matches.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        )}
      </section>

      {/* Skill gaps + Japanese requirement distribution */}
      <div className="grid gap-6 md:grid-cols-2">
        {data.skill_gaps.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Skill gaps</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-4 text-[13px] text-[var(--color-text-secondary)]">
                Skills most often missing from jobs you&apos;d otherwise match.
              </p>
              <BarList
                items={data.skill_gaps.map((gap) => ({ label: gap.skill, value: gap.missing_count }))}
              />
            </CardContent>
          </Card>
        )}

        {data.japanese_requirement_distribution.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Japanese requirement distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-4 text-[13px] text-[var(--color-text-secondary)]">
                Japanese-ability levels requested across open roles.
              </p>
              <BarList
                items={data.japanese_requirement_distribution.map((d) => ({
                  label: d.level,
                  value: d.job_count,
                }))}
              />
            </CardContent>
          </Card>
        )}
      </div>

      {data.skill_gaps.length === 0 && data.japanese_requirement_distribution.length === 0 && (
        <p className="text-[13.5px] text-[var(--color-text-tertiary)]">
          No common skill gaps detected yet.
        </p>
      )}

      {/* Recent alerts */}
      <section>
        <h2 className="text-[17px] font-semibold tracking-tight text-[var(--color-text-primary)]">Recent alerts</h2>
        <Card className="mt-5">
          {data.recent_alerts.length === 0 ? (
            <CardContent className="pt-5">
              <p className="text-[13.5px] text-[var(--color-text-tertiary)]">No alerts yet.</p>
            </CardContent>
          ) : (
            <ul className="divide-y divide-[var(--color-border)]">
              {data.recent_alerts.map((alert) => (
                <AlertRow key={alert.id} alert={alert} />
              ))}
            </ul>
          )}
        </Card>
      </section>
    </div>
  );
}

function AlertRow({ alert }: { alert: NotificationOut }) {
  const Icon = ALERT_ICONS[alert.type] ?? Bell;
  const content = (
    <div className="flex items-start gap-3 px-5 py-4">
      <div className="flex size-8 shrink-0 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)]">
        <Icon className="size-4 text-[var(--color-text-secondary)]" aria-hidden />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-[13.5px] font-medium text-[var(--color-text-primary)]">{alert.title}</p>
        <p className="mt-0.5 truncate text-[13px] text-[var(--color-text-secondary)]">{alert.body}</p>
      </div>
      <span className="shrink-0 whitespace-nowrap text-[12px] text-[var(--color-text-tertiary)]">
        {formatRelativeTime(alert.sent_at)}
      </span>
    </div>
  );

  if (alert.job_id) {
    return (
      <li>
        <Link href={`/jobs/${alert.job_id}`} className="block transition-colors hover:bg-[var(--color-bg-subtle)]">
          {content}
        </Link>
      </li>
    );
  }

  return <li>{content}</li>;
}

function DashboardSkeleton() {
  return (
    <div className="space-y-10">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-4">
          <Skeleton className="h-4 w-40" />
          <Skeleton className="h-4 w-10" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-1.5 w-full" />
          <div className="mt-4 space-y-2">
            <Skeleton className="h-3.5 w-2/3" />
            <Skeleton className="h-3.5 w-1/2" />
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
        {Array.from({ length: 5 }).map((_, i) => (
          <Card key={i} className="p-5">
            <Skeleton className="h-3.5 w-2/3" />
            <Skeleton className="mt-3 h-7 w-10" />
          </Card>
        ))}
      </div>

      <div>
        <Skeleton className="h-5 w-44" />
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          <JobCardSkeleton />
          <JobCardSkeleton />
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {Array.from({ length: 2 }).map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-4 w-32" />
            </CardHeader>
            <CardContent className="space-y-3">
              <Skeleton className="h-2 w-full" />
              <Skeleton className="h-2 w-full" />
              <Skeleton className="h-2 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
