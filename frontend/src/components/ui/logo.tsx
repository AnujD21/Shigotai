import Link from "next/link";
import { cn } from "@/lib/utils";

export function Logo({ className }: { className?: string }) {
  return (
    <Link
      href="/"
      className={cn(
        "group inline-flex items-center gap-2 text-[17px] font-semibold tracking-tight text-[var(--color-text-primary)]",
        className
      )}
    >
      <span className="flex size-7 items-center justify-center rounded-[7px] bg-[var(--color-accent)] font-display text-[14px] font-semibold text-[var(--color-text-on-accent)] shadow-[inset_0_1px_0_rgb(255_255_255/0.2)] transition-transform duration-300 group-hover:-rotate-6">
        仕
      </span>
      Shigotai
    </Link>
  );
}
