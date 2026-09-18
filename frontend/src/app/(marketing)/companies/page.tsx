import type { Metadata } from "next";
import Link from "next/link";
import { Building2 } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import type { CompanySummary } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const metadata: Metadata = {
  title: "Companies — Shigotai",
  description: "Browse Japanese companies with active job listings on Shigotai.",
};

async function getCompanies(): Promise<CompanySummary[]> {
  const res = await fetch(`${API_BASE_URL}/companies`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load companies.");
  return res.json();
}

export default async function CompaniesPage() {
  const companies = await getCompanies();

  return (
    <div className="mx-auto max-w-6xl px-5 py-10 md:px-8">
      <PageHeader title="Companies" description="Japanese companies currently hiring through Shigotai." />

      {companies.length === 0 ? (
        <p className="text-[14px] text-[var(--color-text-secondary)]">No companies listed yet.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
          {companies.map((company) => (
            <Link
              key={company.id}
              href={`/companies/${company.slug}`}
              className="group rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-5 transition-shadow hover:shadow-[var(--shadow-md)]"
            >
              <div className="flex size-9 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)]">
                <Building2 className="size-4 text-[var(--color-text-secondary)]" aria-hidden />
              </div>
              <h2 className="mt-3 text-[15px] font-semibold text-[var(--color-text-primary)] transition-colors group-hover:text-[var(--color-accent)]">
                {company.name}
              </h2>
              <p className="mt-1 text-[13px] text-[var(--color-text-tertiary)]">
                {company.industry ?? "Industry not specified"}
              </p>
              {company.headquarters_location && (
                <p className="mt-0.5 text-[12.5px] text-[var(--color-text-tertiary)]">{company.headquarters_location}</p>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
