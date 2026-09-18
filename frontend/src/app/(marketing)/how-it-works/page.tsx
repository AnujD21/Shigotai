import type { Metadata } from "next";
import {
  BellRing,
  CheckCircle2,
  FileSearch,
  MessageSquareText,
  ScanSearch,
  ShieldCheck,
  Sparkles,
  UserCog,
} from "lucide-react";
import { LinkButton } from "@/components/ui/link-button";
import { FadeIn } from "@/components/motion/fade-in";

export const metadata: Metadata = {
  title: "How it works — Shigotai",
  description:
    "How Shigotai builds your Career DNA, runs a three-stage matching engine against real job requirements, and keeps you notified without the noise.",
};

const PROFILE_POINTS = [
  {
    title: "Structured, not just a resume upload",
    description:
      "Education, work experience, projects, certifications, and skills each get their own fields -- so a strong project or an unusual career path isn't lost inside a PDF.",
  },
  {
    title: "Japanese ability, with nuance",
    description:
      "JLPT level is only part of the picture. Shigotai separately captures speaking, reading, writing, and business Japanese ability, because job postings often ask for one without the others.",
  },
  {
    title: "Preferences that actually filter",
    description:
      "Desired roles, work mode, employment type, salary range, and visa sponsorship needs feed directly into which jobs are worth showing you at all.",
  },
];

const MATCH_STAGES = [
  {
    icon: ScanSearch,
    title: "1. Deterministic requirement check",
    description:
      "Each job's stated requirements -- required skills, minimum experience, education, JLPT level, visa sponsorship -- are checked against your profile as hard facts. This stage never guesses.",
  },
  {
    icon: Sparkles,
    title: "2. Semantic skill matching",
    description:
      "Related and adjacent skills are matched even when the wording differs -- so \"React\" on your profile can register against a posting that asks for \"modern JS frontend frameworks.\"",
  },
  {
    icon: MessageSquareText,
    title: "3. Plain-language explanation",
    description:
      "The result isn't a single score. Every match comes with a breakdown of what you meet, what's uncertain, and what's missing, written in plain language you can act on.",
  },
];

const MONITORING_POINTS = [
  {
    icon: BellRing,
    title: "Background job monitoring",
    description:
      "Shigotai doesn't wait for you to refresh. New postings are matched against your profile as they're found, and existing postings are re-checked for requirement changes.",
  },
  {
    icon: ShieldCheck,
    title: "\"Verified active,\" not just a post date",
    description:
      "Job status is periodically re-confirmed against the source. You'll see when a listing was last verified as still open -- not just when it first appeared, which can be misleading weeks later.",
  },
  {
    icon: FileSearch,
    title: "Notifications tuned to relevance",
    description:
      "You control the threshold: instant alerts, a daily or weekly digest, or nothing at all. Shigotai only surfaces a new match when it's worth interrupting you for.",
  },
];

export default function HowItWorksPage() {
  return (
    <>
      <section className="mx-auto max-w-6xl px-5 pb-16 pt-14 md:px-8 md:pb-24 md:pt-20">
        <FadeIn>
          <p className="text-[12.5px] font-semibold uppercase tracking-wide text-[var(--color-accent)]">
            How it works
          </p>
          <h1 className="mt-2 max-w-2xl text-[32px] font-semibold leading-[1.15] tracking-tight text-[var(--color-text-primary)] md:text-[42px]">
            From your profile to a verified, explained match -- run continuously in the background.
          </h1>
          <p className="mt-5 max-w-xl text-[16px] leading-relaxed text-[var(--color-text-secondary)]">
            Shigotai is built around three ideas: your profile should capture what a resume flattens, matching
            should be checked against facts before anything is inferred, and every result should say exactly why
            it&apos;s there.
          </p>
        </FadeIn>
      </section>

      <section className="border-y border-[var(--color-border)] bg-[var(--color-bg-subtle)]">
        <div className="mx-auto max-w-6xl px-5 py-16 md:px-8 md:py-24">
          <FadeIn>
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-surface)] border border-[var(--color-border)]">
                <UserCog className="size-[18px] text-[var(--color-accent)]" aria-hidden />
              </div>
              <h2 className="text-[24px] font-semibold tracking-tight text-[var(--color-text-primary)] md:text-[28px]">
                Building your Career DNA
              </h2>
            </div>
            <p className="mt-4 max-w-2xl text-[15px] leading-relaxed text-[var(--color-text-secondary)]">
              Your profile is the foundation everything else runs on. It&apos;s more detailed than a resume because it
              needs to answer questions a resume usually can&apos;t.
            </p>
          </FadeIn>
          <div className="mt-10 grid gap-8 md:grid-cols-3 md:gap-6">
            {PROFILE_POINTS.map((point, i) => (
              <FadeIn key={point.title} delay={i * 0.1}>
                <h3 className="text-[15.5px] font-semibold text-[var(--color-text-primary)]">{point.title}</h3>
                <p className="mt-2 text-[14px] leading-relaxed text-[var(--color-text-secondary)]">
                  {point.description}
                </p>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-16 md:px-8 md:py-24">
        <FadeIn>
          <p className="text-[12.5px] font-semibold uppercase tracking-wide text-[var(--color-accent)]">
            The matching engine
          </p>
          <h2 className="mt-2 max-w-xl text-[24px] font-semibold tracking-tight text-[var(--color-text-primary)] md:text-[28px]">
            Three stages, run in order, every time a job is checked against your profile.
          </h2>
        </FadeIn>
        <div className="mt-10 space-y-8">
          {MATCH_STAGES.map((stage, i) => (
            <FadeIn key={stage.title} delay={i * 0.1}>
              <div className="flex gap-5 rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-6">
                <div className="flex size-10 shrink-0 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-bg-subtle)]">
                  <stage.icon className="size-[18px] text-[var(--color-accent)]" aria-hidden />
                </div>
                <div>
                  <h3 className="text-[16px] font-semibold text-[var(--color-text-primary)]">{stage.title}</h3>
                  <p className="mt-1.5 max-w-2xl text-[14.5px] leading-relaxed text-[var(--color-text-secondary)]">
                    {stage.description}
                  </p>
                </div>
              </div>
            </FadeIn>
          ))}
        </div>
      </section>

      <section className="border-y border-[var(--color-border)] bg-[var(--color-bg-subtle)]">
        <div className="mx-auto max-w-6xl px-5 py-16 md:px-8 md:py-24">
          <FadeIn>
            <p className="text-[12.5px] font-semibold uppercase tracking-wide text-[var(--color-accent)]">
              Staying current
            </p>
            <h2 className="mt-2 max-w-xl text-[24px] font-semibold tracking-tight text-[var(--color-text-primary)] md:text-[28px]">
              Monitoring and notifications that respect your attention.
            </h2>
          </FadeIn>
          <div className="mt-10 grid gap-8 md:grid-cols-3 md:gap-6">
            {MONITORING_POINTS.map((point, i) => (
              <FadeIn key={point.title} delay={i * 0.1}>
                <div className="flex size-10 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-surface)] border border-[var(--color-border)]">
                  <point.icon className="size-[18px] text-[var(--color-accent)]" aria-hidden />
                </div>
                <h3 className="mt-4 text-[15.5px] font-semibold text-[var(--color-text-primary)]">{point.title}</h3>
                <p className="mt-2 text-[14px] leading-relaxed text-[var(--color-text-secondary)]">
                  {point.description}
                </p>
              </FadeIn>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-16 md:px-8 md:py-24">
        <FadeIn>
          <div className="flex flex-col items-start gap-6 rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-8 md:flex-row md:items-center md:justify-between md:p-10">
            <div>
              <div className="flex items-center gap-2 text-[13px] font-medium text-[var(--color-success)]">
                <CheckCircle2 className="size-4" aria-hidden />
                Free to start, demo data included
              </div>
              <h2 className="mt-2 max-w-lg text-[22px] font-semibold tracking-tight text-[var(--color-text-primary)] md:text-[26px]">
                Build your profile once. Let the matching run in the background from there.
              </h2>
            </div>
            <LinkButton href="/register" variant="accent" size="lg" className="shrink-0">
              Build My Profile
            </LinkButton>
          </div>
        </FadeIn>
      </section>
    </>
  );
}
