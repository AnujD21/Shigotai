import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { Globe, MapPin, Users } from "lucide-react";
import { JobCard } from "@/components/jobs/job-card";
import { CompanyCompatibilityPanel } from "@/components/jobs/company-compatibility-panel";
import type { CompanyDetail } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function getCompany(slug: string): Promise<CompanyDetail | null> {
  const res = await fetch(`${API_BASE_URL}/companies/${slug}`, { cache: "no-store" });
  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to load company.");
  return res.json();
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const company = await getCompany(slug);
  if (!company) return { title: "Company not found — Shigotai" };
  return {
    title: `${company.name} — Shigotai`,
    description: company.description ?? `${company.name} jobs and hiring info on Shigotai.`,
  };
}

export default async function CompanyDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const company = await getCompany(slug);
  if (!company) notFound();

  return (
    <div className="mx-auto max-w-4xl px-5 py-10 md:px-8">
      <div className="mb-6">
        <Link
          href="/companies"
          className="text-[13px] font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-accent)]"
        >
          ← Back to Companies
        </Link>
      </div>

      <div className="rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-6 md:p-8">
        <h1 className="text-[26px] font-semibold tracking-tight text-[var(--color-text-primary)]">{company.name}</h1>
        <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1.5 text-[13.5px] text-[var(--color-text-tertiary)]">
          {company.industry && <span>{company.industry}</span>}
          {company.headquarters_location && (
            <span className="flex items-center gap-1">
              <MapPin className="size-3.5" aria-hidden /> {company.headquarters_location}
            </span>
          )}
          {company.size_band && (
            <span className="flex items-center gap-1">
              <Users className="size-3.5" aria-hidden /> {company.size_band}
            </span>
          )}
          {company.website && (
            <a
              href={company.website}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-[var(--color-accent)] hover:underline"
            >
              <Globe className="size-3.5" aria-hidden /> Website
            </a>
          )}
        </div>

        {company.tags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {company.tags.map((tag) => (
              <span
                key={tag}
                className="rounded-full border border-[var(--color-border)] bg-[var(--color-bg-subtle)] px-2.5 py-1 text-[12px] text-[var(--color-text-secondary)]"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {company.description && (
          <p className="mt-4 whitespace-pre-line text-[14.5px] leading-relaxed text-[var(--color-text-secondary)]">
            {company.description}
          </p>
        )}
      </div>

      <div className="mt-8">
        <CompanyCompatibilityPanel slug={slug} />
      </div>

      <div className="mt-8">
        <h2 className="text-[17px] font-semibold tracking-tight text-[var(--color-text-primary)]">
          Open positions {company.open_positions.length > 0 && `(${company.open_positions.length})`}
        </h2>
        {company.open_positions.length === 0 ? (
          <p className="mt-4 text-[14px] text-[var(--color-text-secondary)]">No open positions listed right now.</p>
        ) : (
          <div className="mt-5 grid gap-4 md:grid-cols-2">
            {company.open_positions.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
