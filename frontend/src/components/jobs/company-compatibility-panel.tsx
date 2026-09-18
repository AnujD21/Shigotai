"use client";

import useSWR from "swr";
import { ShieldCheck } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LinkButton } from "@/components/ui/link-button";
import { ErrorState } from "@/components/ui/state-views";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/lib/auth-context";
import type { CompanyDetail, CompatibilityBand } from "@/lib/types";

const BAND_TONE: Record<CompatibilityBand["band"], "success" | "info" | "warning" | "neutral"> = {
  STRONG: "success",
  GOOD: "info",
  LIMITED: "warning",
  UNKNOWN: "neutral",
};

export function CompanyCompatibilityPanel({ slug }: { slug: string }) {
  const { user, isLoading: authLoading } = useAuth();

  if (authLoading) {
    return (
      <Card>
        <CardContent className="pt-5">
          <div className="h-16 animate-pulse rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)]" />
        </CardContent>
      </Card>
    );
  }

  if (!user) {
    return (
      <Card>
        <CardContent className="flex flex-col items-start gap-3 pt-5">
          <div className="flex size-9 items-center justify-center rounded-full bg-[var(--color-accent-subtle)]">
            <ShieldCheck className="size-4 text-[var(--color-accent)]" aria-hidden />
          </div>
          <div>
            <p className="text-[15px] font-medium text-[var(--color-text-primary)]">Your compatibility</p>
            <p className="mt-1 text-[13.5px] text-[var(--color-text-secondary)]">
              Log in to see your compatibility with this company, based on your profile.
            </p>
          </div>
          <LinkButton href="/login" variant="accent" size="sm">
            Log in to see your compatibility
          </LinkButton>
        </CardContent>
      </Card>
    );
  }

  return <AuthedCompatibility slug={slug} />;
}

function AuthedCompatibility({ slug }: { slug: string }) {
  const { data, error, isLoading, mutate } = useSWR<CompanyDetail>(`/companies/${slug}`);

  if (isLoading) {
    return (
      <Card>
        <CardContent className="space-y-2.5 pt-5">
          <div className="h-4 w-1/3 animate-pulse rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)]" />
          <div className="h-14 w-full animate-pulse rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)]" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return <ErrorState description="We couldn't load your compatibility with this company." onRetry={() => mutate()} />;
  }

  if (!data || !data.compatibility || data.compatibility.length === 0) {
    return (
      <Card>
        <CardContent className="pt-5">
          <p className="text-[13.5px] text-[var(--color-text-secondary)]">
            Not enough information yet to show your compatibility with this company.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle as="h2">Your compatibility</CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-3">
          {data.compatibility.map((band) => (
            <li
              key={band.label}
              className="flex items-start justify-between gap-4 border-t border-[var(--color-border)] pt-3 first:border-t-0 first:pt-0"
            >
              <div>
                <p className="text-[13.5px] font-medium text-[var(--color-text-primary)]">{band.label}</p>
                <p className="mt-0.5 text-[13px] text-[var(--color-text-tertiary)]">{band.detail}</p>
              </div>
              <Badge tone={BAND_TONE[band.band]}>{band.band}</Badge>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
