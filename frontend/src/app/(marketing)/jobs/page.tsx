import type { Metadata } from "next";
import { Suspense } from "react";
import { PageHeader } from "@/components/ui/page-header";
import { JobCardSkeleton } from "@/components/ui/skeleton";
import { JobsBrowser } from "@/components/jobs/jobs-browser";

export const metadata: Metadata = {
  title: "Discover Jobs — Shigotai",
  description:
    "Search and filter currently active Japan-focused job listings. Log in to see a transparent, requirement-by-requirement match for every role.",
};

export default function JobsPage() {
  return (
    <div className="mx-auto max-w-6xl px-5 py-10 md:px-8">
      <PageHeader
        title="Discover jobs"
        description="Search active listings at Japanese companies. Log in to see how well each one matches your profile."
      />
      <Suspense fallback={<JobsBrowserFallback />}>
        <JobsBrowser />
      </Suspense>
    </div>
  );
}

function JobsBrowserFallback() {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {Array.from({ length: 6 }).map((_, i) => (
        <JobCardSkeleton key={i} />
      ))}
    </div>
  );
}
