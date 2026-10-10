"use client";

import { Fragment } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { LinkButton } from "@/components/ui/link-button";
import { HeroPreview } from "@/components/marketing/hero-preview";
import { LiveStats } from "@/components/marketing/live-stats";
import { EASE_OUT_EXPO } from "@/components/motion/fade-in";

const HEADLINE = ["Find", "the", "Japanese", "jobs", "that", "fit"];

export function Hero() {
  const reduce = useReducedMotion();
  const wordDelay = (i: number) => (reduce ? 0 : 0.08 + i * 0.06);

  return (
    <section className="grain relative overflow-hidden">
      {/* Ambient layers: dot grid + a slow vermillion glow (transform-only drift). */}
      <div className="dot-grid pointer-events-none absolute inset-0 -z-10 opacity-60" aria-hidden />
      <motion.div
        aria-hidden
        className="pointer-events-none absolute -right-40 -top-40 -z-10 size-[620px] rounded-full bg-[radial-gradient(circle,color-mix(in_srgb,var(--color-accent)_22%,transparent),transparent_65%)] blur-2xl"
        animate={reduce ? undefined : { x: [0, -40, 0], y: [0, 30, 0] }}
        transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
      />

      <div className="mx-auto grid max-w-6xl items-center gap-14 px-5 pb-20 pt-14 md:grid-cols-[1.1fr_1fr] md:gap-10 md:px-8 md:pb-28 md:pt-24">
        <div>
          <motion.p
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: EASE_OUT_EXPO }}
            className="mb-6 inline-flex items-center gap-2 rounded-full border border-[var(--color-border)] bg-[var(--color-surface)]/70 px-3 py-1 text-[12.5px] font-medium text-[var(--color-text-secondary)] backdrop-blur-sm"
          >
            <span className="font-display text-[13px] text-[var(--color-accent)]" aria-hidden>
              仕事
            </span>
            Career intelligence for working in Japan
          </motion.p>

          <h1 className="font-display text-[42px] font-semibold leading-[1.08] tracking-[-0.02em] text-[var(--color-text-primary)] sm:text-[52px] md:text-[64px]">
            {HEADLINE.map((word, i) => (
              <Fragment key={word + i}>
                <span className="inline-block overflow-hidden pb-[0.2em] -mb-[0.12em] align-bottom">
                  <motion.span
                    className="inline-block"
                    initial={{ y: reduce ? 0 : "110%", opacity: reduce ? 0 : 1 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.8, delay: wordDelay(i), ease: EASE_OUT_EXPO }}
                  >
                    {word}
                  </motion.span>
                </span>{" "}
              </Fragment>
            ))}
            <span className="relative inline-block overflow-hidden pb-[0.2em] -mb-[0.12em] align-bottom">
              <motion.span
                className="relative inline-block text-[var(--color-accent)]"
                initial={{ y: reduce ? 0 : "110%", opacity: reduce ? 0 : 1 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ duration: 0.8, delay: wordDelay(HEADLINE.length), ease: EASE_OUT_EXPO }}
              >
                you
                {/* Brush underline, drawn after the headline lands. */}
                <svg
                  className="absolute -bottom-[0.06em] left-0 h-[0.22em] w-full overflow-visible"
                  viewBox="0 0 100 12"
                  preserveAspectRatio="none"
                  aria-hidden
                >
                  <motion.path
                    d="M2 9 C 25 3, 55 2, 98 6"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3.5"
                    strokeLinecap="round"
                    initial={{ pathLength: reduce ? 1 : 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 0.7, delay: reduce ? 0 : 0.95, ease: "easeInOut" }}
                  />
                </svg>
              </motion.span>
            </span>
            <span className="text-[var(--color-text-primary)]">.</span>
          </h1>

          <motion.p
            initial={{ opacity: 0, y: reduce ? 0 : 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: reduce ? 0 : 0.55, ease: EASE_OUT_EXPO }}
            className="mt-6 max-w-[34rem] text-[16.5px] leading-relaxed text-[var(--color-text-secondary)] md:text-[17.5px]"
          >
            Shigotai reads live postings from companies hiring in Japan, checks them against your skills, Japanese
            ability, and experience, and tells you exactly why each one fits -- and what&apos;s missing.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: reduce ? 0 : 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: reduce ? 0 : 0.7, ease: EASE_OUT_EXPO }}
            className="mt-9 flex flex-col gap-3 sm:flex-row"
          >
            <LinkButton href="/register" variant="accent" size="lg" className="group">
              Build my profile
              <ArrowRight className="size-4 transition-transform duration-200 group-hover:translate-x-0.5" aria-hidden />
            </LinkButton>
            <LinkButton href="/jobs" variant="outline" size="lg">
              Explore live jobs
            </LinkButton>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: reduce ? 0 : 0.9 }}
            className="mt-6"
          >
            <LiveStats />
          </motion.div>
        </div>

        <div className="relative flex justify-center md:justify-end">
          <span
            aria-hidden
            className="font-display pointer-events-none absolute -left-2 top-4 hidden select-none text-[15px] tracking-[0.5em] text-[var(--color-text-tertiary)]/70 [writing-mode:vertical-rl] lg:block"
          >
            日本で働く
          </span>
          <HeroPreview />
        </div>
      </div>
    </section>
  );
}
