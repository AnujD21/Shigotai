"use client";

import { useRef } from "react";
import { motion, useReducedMotion, useScroll, useSpring } from "framer-motion";
import { BellRing, Sparkles, UserCog } from "lucide-react";
import { FadeIn } from "@/components/motion/fade-in";

const STEPS = [
  {
    icon: UserCog,
    title: "Build your Career DNA",
    description:
      "Upload a resume and confirm what we extract, or fill it in by hand: skills, projects, education, and Japanese ability -- including the parts a resume flattens, like JLPT level versus real business communication.",
  },
  {
    icon: Sparkles,
    title: "Shigotai checks every live posting",
    description:
      "Each role's stated requirements are checked against your profile as hard facts, related skills are matched even when the wording differs, and the result is explained in plain language.",
  },
  {
    icon: BellRing,
    title: "Hear about it when it matters",
    description:
      "New matches -- and roles whose requirements change so that you now qualify -- reach you by email or in-app, without flooding your inbox.",
  },
];

export function HowItWorksSteps() {
  const listRef = useRef<HTMLOListElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: listRef, offset: ["start 75%", "end 55%"] });
  const progress = useSpring(scrollYProgress, { stiffness: 120, damping: 24, restDelta: 0.001 });

  return (
    <section className="mx-auto max-w-6xl px-5 py-20 md:px-8 md:py-28">
      <div className="grid gap-12 md:grid-cols-[0.9fr_1.1fr] md:gap-16">
        <div className="md:sticky md:top-28 md:self-start">
          <FadeIn>
            <p className="text-[12.5px] font-semibold tracking-wide text-[var(--color-accent)]">How it works</p>
            <h2 className="mt-3 font-display text-[30px] font-semibold leading-[1.15] tracking-[-0.01em] text-[var(--color-text-primary)] md:text-[40px]">
              Three steps, then it keeps running in the background.
            </h2>
            <p className="mt-4 max-w-sm text-[15px] leading-relaxed text-[var(--color-text-secondary)]">
              You set up your profile once. New postings are pulled from employers&apos; career boards several times a
              day and matched as they arrive.
            </p>
          </FadeIn>
        </div>

        <ol ref={listRef} className="relative space-y-12 pl-12">
          {/* Track + scroll-linked fill */}
          <span aria-hidden className="absolute bottom-2 left-[15px] top-2 w-px bg-[var(--color-border)]" />
          <motion.span
            aria-hidden
            style={{ scaleY: reduce ? 1 : progress }}
            className="absolute bottom-2 left-[15px] top-2 w-px origin-top bg-[var(--color-accent)]"
          />
          {STEPS.map((step, i) => (
            <li key={step.title} className="relative">
              <FadeIn delay={0.05 * i}>
                <span className="absolute -left-12 top-0 flex size-8 items-center justify-center rounded-full border border-[var(--color-border)] bg-[var(--color-bg)] shadow-[var(--shadow-xs)]">
                  <step.icon className="size-4 text-[var(--color-accent)]" aria-hidden />
                </span>
                <p className="font-display text-[13px] font-semibold tabular-nums text-[var(--color-text-tertiary)]">
                  0{i + 1}
                </p>
                <h3 className="mt-1 text-[19px] font-semibold tracking-tight text-[var(--color-text-primary)]">
                  {step.title}
                </h3>
                <p className="mt-2 max-w-md text-[14.5px] leading-relaxed text-[var(--color-text-secondary)]">
                  {step.description}
                </p>
              </FadeIn>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
