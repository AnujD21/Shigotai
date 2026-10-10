import type { Metadata } from "next";
import { ArrowRight } from "lucide-react";
import { LinkButton } from "@/components/ui/link-button";
import { Hero } from "@/components/marketing/hero";
import { CompanyMarquee } from "@/components/marketing/company-marquee";
import { HowItWorksSteps } from "@/components/marketing/how-it-works-steps";
import { PrinciplesBento } from "@/components/marketing/principles-bento";
import { FadeIn } from "@/components/motion/fade-in";

export const metadata: Metadata = {
  // absolute: the layout's "%s — Shigotai" template would repeat the name.
  title: { absolute: "Shigotai — Find the Japanese jobs that fit you" },
  description:
    "Shigotai analyzes your skills, Japanese ability, education and experience to find currently active opportunities at Japanese companies.",
};

export default function LandingPage() {
  return (
    <>
      <Hero />
      <CompanyMarquee />
      <HowItWorksSteps />
      <PrinciplesBento />

      <section className="mx-auto max-w-6xl px-5 pb-24 md:px-8 md:pb-32">
        <FadeIn>
          <div className="grain relative overflow-hidden rounded-[28px] border border-[var(--color-accent-subtle-border)] bg-[var(--color-accent-subtle)] px-6 py-14 text-center md:px-12 md:py-20">
            <div
              aria-hidden
              className="pointer-events-none absolute left-1/2 top-0 -z-10 size-[520px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(circle,color-mix(in_srgb,var(--color-accent)_28%,transparent),transparent_65%)] blur-2xl"
            />
            <span aria-hidden className="font-display text-[15px] tracking-[0.4em] text-[var(--color-accent)]">
              仕事を見つけよう
            </span>
            <h2 className="mx-auto mt-4 max-w-2xl font-display text-[30px] font-semibold leading-[1.15] tracking-[-0.01em] text-[var(--color-text-primary)] md:text-[44px]">
              Tell Shigotai who you are. We&apos;ll find the companies in Japan hiring for you.
            </h2>
            <p className="mx-auto mt-4 max-w-md text-[15px] leading-relaxed text-[var(--color-text-secondary)]">
              Free to use. Upload your resume and see your first matches in a couple of minutes.
            </p>
            <div className="mt-9 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <LinkButton href="/register" variant="accent" size="lg" className="group">
                Build my profile
                <ArrowRight className="size-4 transition-transform duration-200 group-hover:translate-x-0.5" aria-hidden />
              </LinkButton>
              <LinkButton href="/how-it-works" variant="ghost" size="lg">
                How matching works
              </LinkButton>
            </div>
          </div>
        </FadeIn>
      </section>
    </>
  );
}
