import Link from "next/link";
import { Logo } from "@/components/ui/logo";

export function PublicFooter() {
  return (
    <footer className="border-t border-[var(--color-border)] bg-[var(--color-bg-subtle)]">
      <div className="mx-auto max-w-6xl px-5 py-12 md:px-8">
        <div className="flex flex-col gap-8 md:flex-row md:justify-between">
          <div className="max-w-xs">
            <Logo />
            <p className="mt-3 text-[13.5px] leading-relaxed text-[var(--color-text-secondary)]">
              Career intelligence for people who want to work at Japanese companies.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-8 sm:grid-cols-3">
            <div>
              <p className="mb-3 text-[12px] font-semibold uppercase tracking-wide text-[var(--color-text-tertiary)]">
                Product
              </p>
              <ul className="space-y-2 text-[13.5px]">
                <li><Link href="/jobs" className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">Explore jobs</Link></li>
                <li><Link href="/companies" className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">Companies</Link></li>
                <li><Link href="/how-it-works" className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">How it works</Link></li>
              </ul>
            </div>
            <div>
              <p className="mb-3 text-[12px] font-semibold uppercase tracking-wide text-[var(--color-text-tertiary)]">
                Account
              </p>
              <ul className="space-y-2 text-[13.5px]">
                <li><Link href="/register" className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">Build my profile</Link></li>
                <li><Link href="/login" className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">Log in</Link></li>
              </ul>
            </div>
            <div>
              <p className="mb-3 text-[12px] font-semibold uppercase tracking-wide text-[var(--color-text-tertiary)]">
                About
              </p>
              <ul className="space-y-2 text-[13.5px]">
                <li><Link href="/about" className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">Our approach</Link></li>
              </ul>
            </div>
          </div>
        </div>
        <div className="mt-10 flex flex-col gap-2 border-t border-[var(--color-border)] pt-6 text-[12.5px] text-[var(--color-text-tertiary)] sm:flex-row sm:items-center sm:justify-between">
          <p>&copy; {new Date().getFullYear()} Shigotai. Demo product for illustrative purposes.</p>
          <p>Job listings marked &ldquo;Demo data&rdquo; are fictional and not real postings.</p>
        </div>
      </div>
    </footer>
  );
}
