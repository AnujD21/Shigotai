import Link from "next/link";
import { cn } from "@/lib/utils";

export function Logo({ className }: { className?: string }) {
  return (
    <Link
      href="/"
      className={cn(
        "inline-flex items-center gap-2 text-[17px] font-semibold tracking-tight text-[var(--color-text-primary)]",
        className
      )}
    >
      <span className="flex size-6 items-center justify-center rounded-[5px] bg-[var(--color-text-primary)] text-[12px] font-bold text-[var(--color-bg)]">
        士
      </span>
      Shigotai
    </Link>
  );
}
