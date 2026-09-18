import type { Metadata } from "next";
import { BellRing, FileSearch, ShieldCheck, Sparkles, UserCog } from "lucide-react";
import { LinkButton } from "@/components/ui/link-button";
import { HeroPreview } from "@/components/marketing/hero-preview";
import { FadeIn } from "@/components/motion/fade-in";

export const metadata: Metadata = {
  title: "Shigotai — Find the Japanese jobs that fit you",
  description:
    "Shigotai analyzes your skills, Japanese ability, education and experience to find currently active opportunities at Japanese companies.",
};

const STEPS = [
  {
    icon: UserCog,
    title: "Build your Career DNA",
    description:
      "Skills, projects, education, and Japanese ability -- including the parts a resume usually flattens, like JLPT level versus real business communication.",
  },
  {
    icon: Sparkles,
    title: "Shigotai analyzes the fit",
    description:
      "A deterministic check against stated requirements, then semantic matching for related skills, then a plain-language explanation of what matches and what doesn't.",
  },
  {
    icon: BellRing,
    title: "Get notified when it matters",
    description:
      "New matches and requirement changes reach you by email or in-app, even when you're not on the site -- without flooding your inbox.",
  },
];

const PRINCIPLES = [
  {
    icon: ShieldCheck,
    title: "Transparent, never a mystery score",
    description:
      "Every match shows exactly which requirements you meet, which are uncertain, and which are missing -- not a single opaque percentage.",
  },
  {
    icon: FileSearch,
    title: "Verified activity, not just a post date",
    description:
      "Postings are periodically re-checked against their source. You'll see when a job was last verified as still open, not just when it first appeared.",
  },
];

export default function LandingPage() {
  return (
    <>
      <section className="mx-auto max-w-6xl px-5 pb-16 pt-14 md:px-8 md:pb-24 md:pt-20">
        <div className="grid items-center gap-12 md:grid-cols-2 md:gap-8">
          <div>
            <p className="mb-4 inline-flex items-center rounded-full border border-[var(--color-border)] bg-[var(--color-bg-subtle)] px-3 py-1 text-[12.5px] font-medium text-[var(--color-text-secondary)]">
              Built for candidates targeting Japan
            </p>
            <h1 className="text-[38px] font-semibold leading-[1.1] tracking-tight text-[var(--color-text-primary)] md:text-[52px]">
              Find the Japanese jobs that fit <span className="text-[var(--color-accent)]">you</span>.
            </h1>
            <p className="mt-5 max-w-lg text-[16px] leading-relaxed text-[var(--color-text-secondary)] md:text-[17px]">
              Shigotai analyzes your skills, Japanese ability, education and experience to find currently active
              opportunities at Japanese companies -- and explains exactly why each one fits.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <LinkButton href="/register" variant="accent" size="lg">
                Build My Profile
              </LinkButton>
              <LinkButton href="/jobs" variant="outline" size="lg">
                Explore Jobs
              </LinkButton>
            </div>
            <p className="mt-4 text-[12.5px] text-[var(--color-text-tertiary)]">
              No credit card required. Demo job data included so you can try it immediately.
            </p>
          </div>
          <div className="flex justify-center md:justify-end">
            <HeroPreview />
          </div>
        </div>
      </section>

      <section className="border-y border-[var(--color-border)] bg-[var(--color-bg-subtle)]">
        <div className="mx-auto max-w-6xl px-5 py-16 md:px-8 md:py-24">
          <FadeIn>
            <p className="text-[12.5px] font-semibold uppercase tracking-wide text-[var(--color-accent)]">How it works</p>
            <h2 className="mt-2 max-w-lg text-[26px] font-semibold tracking-tight text-[var(--color-text-primary)] md:text-[32px]">
              Three steps, run continuously in the background.
            </h2>
          </FadeIn>
          <div className="mt-12 grid gap-8 md:grid-cols-3 md:gap-6">
            {STEPS.map((step, i) => (
              <FadeIn key={step.title} delay={i * 0.1}>
                <div className="flex size-10 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-surface)] border border-[var(--color-border)]">
                  <step.icon className="size-[18px] text-[var(--color-accent)]" aria-hidden />
                </div>
                <h3 className="mt-4 text-[16px] font-semibold text-[var(--color-text-primary)]">{step.title}</h3>
                <p className="mt-2 text-[14px] leading-relaxed text-[var(--color-text-secondary)]">{step.description}</p>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-16 md:px-8 md:py-24">
        <div className="grid gap-10 md:grid-cols-2 md:gap-16">
          {PRINCIPLES.map((principle, i) => (
            <FadeIn key={principle.title} delay={i * 0.1}>
              <div className="flex size-10 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)] border border-[var(--color-border)]">
                <principle.icon className="size-[18px] text-[var(--color-text-primary)]" aria-hidden />
              </div>
              <h3 className="mt-4 text-[17px] font-semibold text-[var(--color-text-primary)]">{principle.title}</h3>
              <p className="mt-2 max-w-md text-[14.5px] leading-relaxed text-[var(--color-text-secondary)]">
                {principle.description}
              </p>
            </FadeIn>
          ))}
        </div>
      </section>

      <section className="border-t border-[var(--color-border)]">
        <div className="mx-auto max-w-6xl px-5 py-16 text-center md:px-8 md:py-24">
          <FadeIn>
            <h2 className="mx-auto max-w-xl text-[26px] font-semibold tracking-tight text-[var(--color-text-primary)] md:text-[32px]">
              Tell Shigotai who you are. We&apos;ll find the Japanese companies hiring for you.
            </h2>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <LinkButton href="/register" variant="accent" size="lg">
                Build My Profile
              </LinkButton>
              <LinkButton href="/how-it-works" variant="ghost" size="lg">
                Learn more
              </LinkButton>
            </div>
          </FadeIn>
        </div>
      </section>
    </>
  );
}
