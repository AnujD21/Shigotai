"use client";

import { useState } from "react";
import { Dialog } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import type {
  CertificationEntry,
  EducationEntry,
  ExperienceEntry,
  JLPTLevel,
  ProjectEntry,
  ResumeExtractionResult,
  SkillEntry,
} from "@/lib/types";

export interface AcceptedResumeItems {
  education: EducationEntry[];
  experience: ExperienceEntry[];
  projects: ProjectEntry[];
  certifications: CertificationEntry[];
  skills: SkillEntry[];
  jlpt_level: JLPTLevel | null;
}

function educationLabel(e: EducationEntry) {
  return [e.degree, e.university].filter(Boolean).join(" — ") || "Untitled education entry";
}
function experienceLabel(e: ExperienceEntry) {
  return [e.role, e.company_name].filter(Boolean).join(" at ") || "Untitled experience entry";
}
function projectLabel(p: ProjectEntry) {
  return p.name || "Untitled project";
}
function certLabel(c: CertificationEntry) {
  return [c.name, c.issuer].filter(Boolean).join(" — ") || "Untitled certification";
}

interface GroupItem {
  key: string;
  label: string;
}

function initialChecked(result: ResumeExtractionResult | null): Record<string, boolean> {
  if (!result) return {};
  const next: Record<string, boolean> = {};
  result.education.forEach((_, i) => (next[`education-${i}`] = true));
  result.experience.forEach((_, i) => (next[`experience-${i}`] = true));
  result.projects.forEach((_, i) => (next[`projects-${i}`] = true));
  result.certifications.forEach((_, i) => (next[`certifications-${i}`] = true));
  result.skills.forEach((_, i) => (next[`skills-${i}`] = true));
  if (result.jlpt_level && result.jlpt_level !== "NONE") next["jlpt-0"] = true;
  return next;
}

export function ResumeReviewDialog({
  result,
  onClose,
  onConfirm,
}: {
  result: ResumeExtractionResult | null;
  onClose: () => void;
  onConfirm: (accepted: AcceptedResumeItems) => void;
}) {
  const [checked, setChecked] = useState<Record<string, boolean>>(() => initialChecked(result));
  const [trackedResult, setTrackedResult] = useState(result);

  // Reset the toggle state whenever a new extraction result arrives, following
  // React's "adjusting state when a prop changes" pattern (no effect needed).
  if (result !== trackedResult) {
    setTrackedResult(result);
    setChecked(initialChecked(result));
  }

  if (!result) return null;

  function toggle(key: string) {
    setChecked((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  function handleConfirm() {
    if (!result) return;
    onConfirm({
      education: result.education.filter((_, i) => checked[`education-${i}`]),
      experience: result.experience.filter((_, i) => checked[`experience-${i}`]),
      projects: result.projects.filter((_, i) => checked[`projects-${i}`]),
      certifications: result.certifications.filter((_, i) => checked[`certifications-${i}`]),
      skills: result.skills.filter((_, i) => checked[`skills-${i}`]),
      jlpt_level: checked["jlpt-0"] ? result.jlpt_level : null,
    });
  }

  const groups: { key: string; title: string; items: GroupItem[] }[] = [
    {
      key: "education",
      title: "Education",
      items: result.education.map((e, i) => ({ key: `education-${i}`, label: educationLabel(e) })),
    },
    {
      key: "experience",
      title: "Experience",
      items: result.experience.map((e, i) => ({ key: `experience-${i}`, label: experienceLabel(e) })),
    },
    {
      key: "projects",
      title: "Projects",
      items: result.projects.map((p, i) => ({ key: `projects-${i}`, label: projectLabel(p) })),
    },
    {
      key: "certifications",
      title: "Certifications",
      items: result.certifications.map((c, i) => ({ key: `certifications-${i}`, label: certLabel(c) })),
    },
    {
      key: "skills",
      title: "Skills",
      items: result.skills.map((s, i) => ({
        key: `skills-${i}`,
        label: s.is_ai_ml ? `${s.name} (AI/ML)` : s.name,
      })),
    },
  ];
  if (result.jlpt_level && result.jlpt_level !== "NONE") {
    groups.push({ key: "jlpt", title: "Japanese level", items: [{ key: "jlpt-0", label: `JLPT ${result.jlpt_level}` }] });
  }

  const hasAnyItems = groups.some((g) => g.items.length > 0);

  return (
    <Dialog open={!!result} onClose={onClose} title="We found these details in your resume">
      <div className="space-y-5">
        <p className="text-[13px] text-[var(--color-text-secondary)]">
          Review what we found. Uncheck anything you don&apos;t want to add — nothing is saved to your profile until
          you confirm here and then click Save changes below.
        </p>

        {result.warnings.length > 0 && (
          <ul className="space-y-1 rounded-[var(--radius-sm)] bg-[var(--color-warning-subtle)] p-3 text-[12.5px] text-[var(--color-warning)]">
            {result.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        )}

        {!hasAnyItems && (
          <p className="text-[13.5px] text-[var(--color-text-tertiary)]">
            We couldn&apos;t extract any structured details from this file.
          </p>
        )}

        {groups.map((group) =>
          group.items.length > 0 ? (
            <div key={group.key}>
              <p className="mb-2 text-[12px] font-semibold uppercase tracking-wide text-[var(--color-text-tertiary)]">
                {group.title}
              </p>
              <div className="space-y-2">
                {group.items.map((item) => (
                  <div
                    key={item.key}
                    className="flex items-center justify-between gap-3 rounded-[var(--radius-sm)] border border-[var(--color-border)] px-3 py-2"
                  >
                    <span className="text-[13.5px] text-[var(--color-text-primary)]">{item.label}</span>
                    <Checkbox
                      checked={!!checked[item.key]}
                      onChange={() => toggle(item.key)}
                      aria-label={`Add ${item.label}`}
                    />
                  </div>
                ))}
              </div>
            </div>
          ) : null
        )}

        <div className="flex justify-end gap-3 border-t border-[var(--color-border)] pt-4">
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="button" variant="accent" onClick={handleConfirm} disabled={!hasAnyItems}>
            Add selected
          </Button>
        </div>
      </div>
    </Dialog>
  );
}
