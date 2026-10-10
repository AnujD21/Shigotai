"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  AlertTriangle,
  CheckCircle2,
  CircleDot,
  Languages,
  Radar,
  ShieldCheck,
  Sparkles,
  XCircle,
} from "lucide-react";
import { SpotlightCard } from "@/components/motion/spotlight-card";
import { Stagger, StaggerItem } from "@/components/motion/stagger";
import { cn } from "@/lib/utils";

function Tile({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <StaggerItem className={className}>
      <SpotlightCard className="flex h-full flex-col rounded-[20px] border border-[var(--color-border)] bg-[var(--color-surface)] p-6 shadow-[var(--shadow-xs)] transition-shadow duration-300 hover:shadow-[var(--shadow-md)] md:p-7">
        {children}
      </SpotlightCard>
    </StaggerItem>
  );
}

function TileHeading({ icon: Icon, title, children }: { icon: typeof ShieldCheck; title: string; children: React.ReactNode }) {
  return (
    <div>
      <span className="flex size-9 items-center justify-center rounded-[10px] bg-[var(--color-accent-subtle)]">
        <Icon className="size-[18px] text-[var(--color-accent)]" aria-hidden />
      </span>
      <h3 className="mt-4 text-[17px] font-semibold tracking-tight text-[var(--color-text-primary)]">{title}</h3>
      <p className="mt-1.5 max-w-md text-[14px] leading-relaxed text-[var(--color-text-secondary)]">{children}</p>
    </div>
  );
}

const BREAKDOWN = [
  { icon: CheckCircle2, tone: "text-[var(--color-success)]", label: "Python, PyTorch", detail: "Required -- you have both" },
  { icon: CheckCircle2, tone: "text-[var(--color-success)]", label: "Bachelor's degree", detail: "Meets stated requirement" },
  { icon: AlertTriangle, tone: "text-[var(--color-warning)]", label: "Business Japanese", detail: "No JLPT level stated -- you're N3" },
  { icon: XCircle, tone: "text-[var(--color-text-tertiary)]", label: "Kubernetes", detail: "Preferred, not required" },
];

const TIMELINE = [
  { label: "First seen", detail: "Posted on the employer's board, 4 days ago" },
  { label: "Re-verified", detail: "Still listed, 2 hours ago" },
  { label: "Closed", detail: "Marked closed the moment it comes down" },
];

const LANGUAGE = [
  { label: "JLPT", value: "N3", fill: 0.6 },
  { label: "Speaking", value: "Conversational", fill: 0.5 },
  { label: "Business Japanese", value: "Basic", fill: 0.25 },
];

export function PrinciplesBento() {
  const reduce = useReducedMotion();

  return (
    <section className="mx-auto max-w-6xl px-5 pb-20 md:px-8 md:pb-28">
      <div className="mb-10 max-w-xl">
        <p className="text-[12.5px] font-semibold tracking-wide text-[var(--color-accent)]">What makes it different</p>
        <h2 className="mt-3 font-display text-[30px] font-semibold leading-[1.15] tracking-[-0.01em] text-[var(--color-text-primary)] md:text-[40px]">
          Built to be trusted, not just clicked.
        </h2>
      </div>

      <Stagger className="grid gap-4 md:grid-cols-6 md:grid-rows-[auto_auto]">
        <Tile className="md:col-span-3 md:row-span-2">
          <TileHeading icon={ShieldCheck} title="Transparent, never a mystery score">
            Every match shows which requirements you meet, which are uncertain, and which are missing -- not a single
            opaque percentage.
          </TileHeading>
          <ul className="mt-6 space-y-2 rounded-[14px] border border-[var(--color-border)] bg-[var(--color-bg)] p-4">
            {BREAKDOWN.map((row, i) => (
              <motion.li
                key={row.label}
                initial={{ opacity: 0, x: reduce ? 0 : -6 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.25 + i * 0.1, duration: 0.4 }}
                className="flex items-start gap-2.5 text-[13.5px]"
              >
                <row.icon className={cn("mt-0.5 size-4 shrink-0", row.tone)} aria-hidden />
                <span>
                  <span className="text-[var(--color-text-primary)]">{row.label}</span>
                  <span className="ml-2 text-[12.5px] text-[var(--color-text-tertiary)]">{row.detail}</span>
                </span>
              </motion.li>
            ))}
          </ul>
          <motion.div
            initial={{ opacity: 0, y: reduce ? 0 : 6 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.75, duration: 0.5 }}
            className="mt-4 rounded-[14px] border border-dashed border-[var(--color-border-strong)] px-4 py-3.5"
          >
            <p className="flex items-center gap-1.5 text-[11.5px] font-semibold uppercase tracking-wide text-[var(--color-text-tertiary)]">
              <Sparkles className="size-3 text-[var(--color-accent)]" aria-hidden />
              In plain language
            </p>
            <p className="mt-1.5 text-[13px] leading-relaxed text-[var(--color-text-secondary)]">
              You meet both required skills and the degree requirement. The role asks for business-level Japanese
              without naming a JLPT level, so check the interview language before applying.
            </p>
          </motion.div>
          <p className="mt-auto pt-6 text-[12.5px] text-[var(--color-text-tertiary)]">
            If a posting doesn&apos;t state a JLPT level, we never invent one.
          </p>
        </Tile>

        <Tile className="md:col-span-3">
          <TileHeading icon={Radar} title="Verified activity, not just a post date">
            Postings come from employers&apos; own career boards and are re-checked several times a day.
          </TileHeading>
          <ol className="mt-5 flex flex-col gap-3 sm:flex-row sm:gap-2">
            {TIMELINE.map((step, i) => (
              <li key={step.label} className="flex-1">
                <div className="flex items-center gap-2">
                  <CircleDot
                    className={cn(
                      "size-3.5 shrink-0",
                      i === 2 ? "text-[var(--color-text-tertiary)]" : "text-[var(--color-success)]"
                    )}
                    aria-hidden
                  />
                  <span className="text-[13px] font-medium text-[var(--color-text-primary)]">{step.label}</span>
                </div>
                <p className="mt-1 pl-[22px] text-[12.5px] leading-snug text-[var(--color-text-tertiary)]">{step.detail}</p>
              </li>
            ))}
          </ol>
        </Tile>

        <Tile className="md:col-span-3">
          <TileHeading icon={Languages} title="Japanese ability, in detail">
            JLPT isn&apos;t the whole story. Speaking, reading, writing, and business Japanese are tracked separately,
            because postings ask for them separately.
          </TileHeading>
          <div className="mt-5 space-y-2.5">
            {LANGUAGE.map((row, i) => (
              <div key={row.label} className="grid grid-cols-[8.5rem_1fr_auto] items-center gap-3 text-[12.5px]">
                <span className="text-[var(--color-text-secondary)]">{row.label}</span>
                <span className="h-1.5 overflow-hidden rounded-full bg-[var(--color-bg-subtle)]">
                  <motion.span
                    className="block h-full origin-left rounded-full bg-[var(--color-info)]"
                    initial={{ scaleX: reduce ? row.fill : 0 }}
                    whileInView={{ scaleX: row.fill }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 + i * 0.1, duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                  />
                </span>
                <span className="font-medium text-[var(--color-text-primary)]">{row.value}</span>
              </div>
            ))}
          </div>
        </Tile>
      </Stagger>
    </section>
  );
}
