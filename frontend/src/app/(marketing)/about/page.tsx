import type { Metadata } from "next";
import { AlertTriangle, CheckCircle2, CircleDashed, FlaskConical, Languages } from "lucide-react";
import { LinkButton } from "@/components/ui/link-button";
import { FadeIn } from "@/components/motion/fade-in";

export const metadata: Metadata = {
  title: "About — Shigotai",
  description:
    "Why Shigotai exists: closing the gap between resumes and what Japanese employers actually state as requirements, with transparent fact-vs-interpretation matching.",
};

const SIGNAL_STATES = [
  {
    icon: CheckCircle2,
    label: "FACT",
    tone: "text-[var(--color-success)]",
    description: "Stated directly in the posting and checked deterministically against your profile -- no inference involved.",
  },
  {
    icon: FlaskConical,
    label: "AI INTERPRETATION",
    tone: "text-[var(--color-accent)]",
    description: "A reasonable read on related or adjacent experience, clearly labeled as an interpretation, not a certainty.",
  },
  {
    icon: CircleDashed,
    label: "UNKNOWN",
    tone: "text-[var(--color-text-tertiary)]",
    description: "The posting simply doesn't say. Shigotai tells you that plainly instead of quietly assuming an answer.",
  },
];

export default function AboutPage() {
  return (
    <>
      <section className="mx-auto max-w-6xl px-5 pb-16 pt-14 md:px-8 md:pb-24 md:pt-20">
        <FadeIn>
          <p className="text-[12.5px] font-semibold uppercase tracking-wide text-[var(--color-accent)]">
            Our approach
          </p>
          <h1 className="mt-2 max-w-2xl text-[32px] font-semibold leading-[1.15] tracking-tight text-[var(--color-text-primary)] md:text-[42px]">
            Job hunting in Japan runs on details resumes weren&apos;t built to carry.
          </h1>
          <p className="mt-5 max-w-xl text-[16px] leading-relaxed text-[var(--color-text-secondary)]">
            Shigotai exists to close the gap between what a candidate actually offers and what a job posting
            actually asks for -- especially the parts that get lost in translation between the two.
          </p>
        </FadeIn>
      </section>

      <section className="border-y border-[var(--color-border)] bg-[var(--color-bg-subtle)]">
        <div className="mx-auto max-w-6xl px-5 py-16 md:px-8 md:py-24">
          <FadeIn>
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-surface)] border border-[var(--color-border)]">
                <Languages className="size-[18px] text-[var(--color-accent)]" aria-hidden />
              </div>
              <h2 className="text-[24px] font-semibold tracking-tight text-[var(--color-text-primary)] md:text-[28px]">
                The Japanese-ability gap
              </h2>
            </div>
            <p className="mt-4 max-w-2xl text-[15px] leading-relaxed text-[var(--color-text-secondary)]">
              A JLPT level on a resume rarely tells an employer what they actually need to know: can you read
              internal documents, hold a meeting, or write a client email. Postings state requirements with the
              same ambiguity, mixing JLPT levels with vague phrases like &ldquo;business-level Japanese.&rdquo;
              Shigotai treats speaking, reading, writing, and business Japanese as separate signals on both sides
              of the match, instead of compressing them into one number that satisfies neither.
            </p>
          </FadeIn>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-16 md:px-8 md:py-24">
        <FadeIn>
          <p className="text-[12.5px] font-semibold uppercase tracking-wide text-[var(--color-accent)]">
            A principle, not a score
          </p>
          <h2 className="mt-2 max-w-xl text-[24px] font-semibold tracking-tight text-[var(--color-text-primary)] md:text-[28px]">
            Every requirement is FACT, AI INTERPRETATION, or UNKNOWN -- never a mystery percentage.
          </h2>
          <p className="mt-4 max-w-2xl text-[15px] leading-relaxed text-[var(--color-text-secondary)]">
            A single match score hides more than it reveals. Shigotai shows its work instead: which requirements
            you clearly meet, which are a reasonable inference from adjacent experience, and which the posting
            simply never addresses.
          </p>
        </FadeIn>
        <div className="mt-10 grid gap-8 md:grid-cols-3 md:gap-6">
          {SIGNAL_STATES.map((state, i) => (
            <FadeIn key={state.label} delay={i * 0.1}>
              <div className="flex items-center gap-2">
                <state.icon className={`size-[18px] ${state.tone}`} aria-hidden />
                <span className={`text-[13px] font-semibold uppercase tracking-wide ${state.tone}`}>
                  {state.label}
                </span>
              </div>
              <p className="mt-2.5 text-[14px] leading-relaxed text-[var(--color-text-secondary)]">
                {state.description}
              </p>
            </FadeIn>
          ))}
        </div>
      </section>

      <section className="border-y border-[var(--color-border)] bg-[var(--color-bg-subtle)]">
        <div className="mx-auto max-w-6xl px-5 py-16 md:px-8 md:py-24">
          <FadeIn>
            <div className="flex items-center gap-3">
              <div className="flex size-10 items-center justify-center rounded-[var(--radius-sm)] bg-[var(--color-surface)] border border-[var(--color-border)]">
                <AlertTriangle className="size-[18px] text-[var(--color-text-primary)]" aria-hidden />
              </div>
              <h2 className="text-[20px] font-semibold tracking-tight text-[var(--color-text-primary)] md:text-[22px]">
                About the data you&apos;ll see
              </h2>
            </div>
            <p className="mt-4 max-w-2xl text-[14.5px] leading-relaxed text-[var(--color-text-secondary)]">
              This environment can include job listings clearly marked &ldquo;Demo data&rdquo; alongside real
              postings, so the matching experience can be explored end-to-end without waiting on live coverage of
              every company. Demo listings are always labeled on the job itself -- never presented as a real,
              currently open role.
            </p>
          </FadeIn>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-5 py-16 text-center md:px-8 md:py-24">
        <FadeIn>
          <h2 className="mx-auto max-w-xl text-[26px] font-semibold tracking-tight text-[var(--color-text-primary)] md:text-[32px]">
            See what a transparent match actually looks like.
          </h2>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <LinkButton href="/register" variant="accent" size="lg">
              Build My Profile
            </LinkButton>
            <LinkButton href="/jobs" variant="ghost" size="lg">
              Explore Jobs
            </LinkButton>
          </div>
        </FadeIn>
      </section>
    </>
  );
}
