"use client";

import { Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input, Label } from "@/components/ui/input";
import { EmptyState } from "@/components/ui/state-views";
import type { EducationEntry } from "@/lib/types";

export type EditableEducation = EducationEntry & { _key: string };

export function newEducationRow(): EditableEducation {
  return {
    _key: crypto.randomUUID(),
    degree: "",
    university: "",
    field_of_study: "",
    graduation_year: null,
    is_current_student: false,
  };
}

export function EducationSection({
  items,
  onChange,
}: {
  items: EditableEducation[];
  onChange: (items: EditableEducation[]) => void;
}) {
  function updateRow(key: string, patch: Partial<EditableEducation>) {
    onChange(items.map((item) => (item._key === key ? { ...item, ...patch } : item)));
  }

  function removeRow(key: string) {
    onChange(items.filter((item) => item._key !== key));
  }

  return (
    <div className="space-y-4">
      {items.length === 0 && (
        <EmptyState title="No education added yet" description="Add your degrees or ongoing studies." />
      )}
      {items.map((item) => (
        <div key={item._key} className="relative rounded-[var(--radius-md)] border border-[var(--color-border)] p-4">
          <button
            type="button"
            onClick={() => removeRow(item._key)}
            aria-label="Remove education entry"
            className="absolute right-3 top-3 flex size-7 items-center justify-center rounded-[var(--radius-sm)] text-[var(--color-text-tertiary)] hover:bg-[var(--color-danger-subtle)] hover:text-[var(--color-danger)]"
          >
            <Trash2 className="size-4" aria-hidden />
          </button>
          <div className="grid gap-4 pr-8 sm:grid-cols-2">
            <div>
              <Label htmlFor={`edu-degree-${item._key}`}>Degree</Label>
              <Input
                id={`edu-degree-${item._key}`}
                value={item.degree}
                onChange={(e) => updateRow(item._key, { degree: e.target.value })}
                placeholder="B.S. Computer Science"
              />
            </div>
            <div>
              <Label htmlFor={`edu-university-${item._key}`}>University</Label>
              <Input
                id={`edu-university-${item._key}`}
                value={item.university}
                onChange={(e) => updateRow(item._key, { university: e.target.value })}
                placeholder="University of Tokyo"
              />
            </div>
            <div>
              <Label htmlFor={`edu-field-${item._key}`}>Field of study</Label>
              <Input
                id={`edu-field-${item._key}`}
                value={item.field_of_study ?? ""}
                onChange={(e) => updateRow(item._key, { field_of_study: e.target.value })}
                placeholder="Computer Science"
              />
            </div>
            <div>
              <Label htmlFor={`edu-year-${item._key}`}>Graduation year</Label>
              <Input
                id={`edu-year-${item._key}`}
                type="number"
                inputMode="numeric"
                value={item.graduation_year ?? ""}
                onChange={(e) =>
                  updateRow(item._key, { graduation_year: e.target.value ? Number(e.target.value) : null })
                }
                placeholder="2025"
              />
            </div>
          </div>
          <div className="mt-3">
            <Checkbox
              label="Currently studying"
              checked={item.is_current_student}
              onChange={(e) => updateRow(item._key, { is_current_student: e.target.checked })}
            />
          </div>
        </div>
      ))}
      <Button type="button" variant="outline" size="sm" onClick={() => onChange([...items, newEducationRow()])}>
        <Plus className="size-4" aria-hidden />
        Add education
      </Button>
    </div>
  );
}
