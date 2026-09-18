"use client";

import { Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input, Label, Textarea } from "@/components/ui/input";
import { EmptyState } from "@/components/ui/state-views";
import type { ExperienceEntry } from "@/lib/types";

export type EditableExperience = ExperienceEntry & { _key: string };

export function newExperienceRow(): EditableExperience {
  return {
    _key: crypto.randomUUID(),
    company_name: "",
    role: "",
    is_internship: false,
    start_date: "",
    end_date: "",
    description: "",
  };
}

export function ExperienceSection({
  items,
  onChange,
}: {
  items: EditableExperience[];
  onChange: (items: EditableExperience[]) => void;
}) {
  function updateRow(key: string, patch: Partial<EditableExperience>) {
    onChange(items.map((item) => (item._key === key ? { ...item, ...patch } : item)));
  }

  function removeRow(key: string) {
    onChange(items.filter((item) => item._key !== key));
  }

  return (
    <div className="space-y-4">
      {items.length === 0 && (
        <EmptyState title="No experience added yet" description="Add internships, jobs, or research roles." />
      )}
      {items.map((item) => (
        <div key={item._key} className="relative rounded-[var(--radius-md)] border border-[var(--color-border)] p-4">
          <button
            type="button"
            onClick={() => removeRow(item._key)}
            aria-label="Remove experience entry"
            className="absolute right-3 top-3 flex size-7 items-center justify-center rounded-[var(--radius-sm)] text-[var(--color-text-tertiary)] hover:bg-[var(--color-danger-subtle)] hover:text-[var(--color-danger)]"
          >
            <Trash2 className="size-4" aria-hidden />
          </button>
          <div className="grid gap-4 pr-8 sm:grid-cols-2">
            <div>
              <Label htmlFor={`exp-company-${item._key}`}>Company</Label>
              <Input
                id={`exp-company-${item._key}`}
                value={item.company_name}
                onChange={(e) => updateRow(item._key, { company_name: e.target.value })}
                placeholder="Acme Corp"
              />
            </div>
            <div>
              <Label htmlFor={`exp-role-${item._key}`}>Role</Label>
              <Input
                id={`exp-role-${item._key}`}
                value={item.role}
                onChange={(e) => updateRow(item._key, { role: e.target.value })}
                placeholder="Software Engineer"
              />
            </div>
            <div>
              <Label htmlFor={`exp-start-${item._key}`}>Start date</Label>
              <Input
                id={`exp-start-${item._key}`}
                value={item.start_date ?? ""}
                onChange={(e) => updateRow(item._key, { start_date: e.target.value })}
                placeholder="2023-04"
              />
            </div>
            <div>
              <Label htmlFor={`exp-end-${item._key}`}>End date</Label>
              <Input
                id={`exp-end-${item._key}`}
                value={item.end_date ?? ""}
                onChange={(e) => updateRow(item._key, { end_date: e.target.value })}
                placeholder="2024-03 or Present"
              />
            </div>
          </div>
          <div className="mt-4">
            <Label htmlFor={`exp-desc-${item._key}`}>Description</Label>
            <Textarea
              id={`exp-desc-${item._key}`}
              value={item.description ?? ""}
              onChange={(e) => updateRow(item._key, { description: e.target.value })}
              placeholder="What did you build or contribute?"
            />
          </div>
          <div className="mt-3">
            <Checkbox
              label="This was an internship"
              checked={item.is_internship}
              onChange={(e) => updateRow(item._key, { is_internship: e.target.checked })}
            />
          </div>
        </div>
      ))}
      <Button type="button" variant="outline" size="sm" onClick={() => onChange([...items, newExperienceRow()])}>
        <Plus className="size-4" aria-hidden />
        Add experience
      </Button>
    </div>
  );
}
