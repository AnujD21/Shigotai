import type { Metadata } from "next";
import { ArrowLeft, Search } from "lucide-react";
import { Logo } from "@/components/ui/logo";
import { LinkButton } from "@/components/ui/link-button";

export const metadata: Metadata = {
  title: "Page not found",
};

export default function NotFound() {
  return (
    <div className="grain relative flex min-h-screen flex-col overflow-hidden">
      <div className="dot-grid pointer-events-none absolute inset-0 -z-10 opacity-50" aria-hidden />
      <header className="mx-auto w-full max-w-6xl px-5 py-5 md:px-8">
        <Logo />
      </header>
      <main id="main-content" className="flex flex-1 items-center justify-center px-5 pb-24">
        <div className="max-w-md text-center">
          <p aria-hidden className="font-display text-[88px] font-semibold leading-none text-[var(--color-accent)] md:text-[112px]">
            404
          </p>
          <h1 className="mt-4 font-display text-[26px] font-semibold tracking-[-0.01em] text-[var(--color-text-primary)]">
            This page isn&apos;t here
          </h1>
          <p className="mt-3 text-[15px] leading-relaxed text-[var(--color-text-secondary)]">
            The link may be broken, or the job you&apos;re looking for has been taken down by the employer.
          </p>
          <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
            <LinkButton href="/jobs" variant="accent">
              <Search className="size-4" aria-hidden />
              Browse open jobs
            </LinkButton>
            <LinkButton href="/" variant="outline">
              <ArrowLeft className="size-4" aria-hidden />
              Back to home
            </LinkButton>
          </div>
        </div>
      </main>
    </div>
  );
}
