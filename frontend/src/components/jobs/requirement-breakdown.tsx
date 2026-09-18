import { RequirementIcon } from "@/components/ui/status-indicator";
import type { RequirementItem } from "@/lib/types";

const CATEGORY_LABELS: Record<string, string> = {
  language: "Japanese",
  education: "Education",
  experience: "Experience",
  required_skill: "Required skills",
  preferred_skill: "Preferred skills",
  eligibility: "Eligibility",
  visa: "Visa",
  location: "Location",
};

export function RequirementBreakdown({ items }: { items: RequirementItem[] }) {
  if (items.length === 0) {
    return (
      <p className="text-sm text-[var(--color-text-secondary)]">
        Not enough information in your profile yet to compare against this role.
      </p>
    );
  }

  const grouped = items.reduce<Record<string, RequirementItem[]>>((acc, item) => {
    (acc[item.category] ??= []).push(item);
    return acc;
  }, {});

  return (
    <div className="space-y-5">
      {Object.entries(grouped).map(([category, rows]) => (
        <div key={category}>
          <p className="mb-2 text-[12px] font-semibold uppercase tracking-wide text-[var(--color-text-tertiary)]">
            {CATEGORY_LABELS[category] ?? category}
          </p>
          <ul className="space-y-2">
            {rows.map((row, idx) => (
              <li key={`${row.label}-${idx}`} className="flex items-start gap-2.5 text-[14px]">
                <RequirementIcon state={row.state} className="mt-0.5" />
                <div>
                  <span className="text-[var(--color-text-primary)]">{row.label}</span>
                  {row.detail && <span className="ml-2 text-[13px] text-[var(--color-text-tertiary)]">{row.detail}</span>}
                </div>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
