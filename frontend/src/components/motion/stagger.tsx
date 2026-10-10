"use client";

import { motion, useReducedMotion, type Variants } from "framer-motion";
import type { ReactNode } from "react";
import { EASE_OUT_EXPO } from "@/components/motion/fade-in";

/**
 * Children wrapped in <StaggerItem> cascade in one after another, either
 * when scrolled into view (default) or immediately on mount.
 */
export function Stagger({
  children,
  className,
  stagger = 0.07,
  delay = 0,
  onMount = false,
  as = "div",
}: {
  children: ReactNode;
  className?: string;
  stagger?: number;
  delay?: number;
  onMount?: boolean;
  as?: "div" | "ul" | "ol";
}) {
  const variants: Variants = {
    hidden: {},
    show: { transition: { staggerChildren: stagger, delayChildren: delay } },
  };
  const Component = motion[as];
  const trigger = onMount ? { animate: "show" } : { whileInView: "show", viewport: { once: true, margin: "-60px" } };
  return (
    <Component className={className} variants={variants} initial="hidden" {...trigger}>
      {children}
    </Component>
  );
}

export function StaggerItem({
  children,
  className,
  y = 14,
  as = "div",
}: {
  children: ReactNode;
  className?: string;
  y?: number;
  as?: "div" | "li";
}) {
  const reduce = useReducedMotion();
  const variants: Variants = {
    hidden: { opacity: 0, y: reduce ? 0 : y },
    show: { opacity: 1, y: 0, transition: { duration: reduce ? 0.2 : 0.6, ease: EASE_OUT_EXPO } },
  };
  const Component = motion[as];
  return (
    <Component className={className} variants={variants}>
      {children}
    </Component>
  );
}
