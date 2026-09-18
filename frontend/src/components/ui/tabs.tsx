"use client";

import { cn } from "@/lib/utils";

export function Tabs({
  tabs,
  active,
  onChange,
  className,
}: {
  tabs: { value: string; label: string; count?: number }[];
  active: string;
  onChange: (value: string) => void;
  className?: string;
}) {
  return (
    <div role="tablist" className={cn("flex items-center gap-1 border-b border-[var(--color-border)]", className)}>
      {tabs.map((tab) => {
        const isActive = tab.value === active;
        return (
          <button
            key={tab.value}
            role="tab"
            aria-selected={isActive}
            onClick={() => onChange(tab.value)}
            className={cn(
              "relative px-3.5 py-2.5 text-[13.5px] font-medium text-[var(--color-text-tertiary)] transition-colors hover:text-[var(--color-text-primary)]",
              isActive && "text-[var(--color-text-primary)]"
            )}
          >
            {tab.label}
            {typeof tab.count === "number" && (
              <span className="ml-1.5 text-[var(--color-text-tertiary)]">({tab.count})</span>
            )}
            {isActive && (
              <span className="absolute inset-x-0 -bottom-px h-[2px] rounded-full bg-[var(--color-accent)]" />
            )}
          </button>
        );
      })}
    </div>
  );
}
