import { Badge } from "@/components/ui/badge";
import type { MatchStrength } from "@/lib/types";

const CONFIG: Record<MatchStrength, { label: string; tone: "success" | "warning" | "neutral" }> = {
  STRONG_MATCH: { label: "Strong match", tone: "success" },
  PARTIAL_MATCH: { label: "Partial match", tone: "warning" },
  SIGNIFICANT_GAPS: { label: "Significant gaps", tone: "neutral" },
};

export function MatchStrengthBadge({ strength }: { strength: MatchStrength | null }) {
  if (!strength) return null;
  const config = CONFIG[strength];
  return <Badge tone={config.tone}>{config.label}</Badge>;
}
