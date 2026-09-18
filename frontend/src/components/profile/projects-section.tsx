"use client";

import { Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input, Label, Textarea } from "@/components/ui/input";
import { EmptyState } from "@/components/ui/state-views";
import { TagInput } from "@/components/ui/tag-input";
import type { ProjectEntry } from "@/lib/types";

export type EditableProject = ProjectEntry & { _key: string };

export function newProjectRow(): EditableProject {
  return {
    _key: crypto.randomUUID(),
    name: "",
    description: "",
    technologies: [],
    role: "",
    github_url: "",
    project_url: "",
    duration: "",
  };
}

export function ProjectsSection({
  items,
  onChange,
}: {
  items: EditableProject[];
  onChange: (items: EditableProject[]) => void;
}) {
  function updateRow(key: string, patch: Partial<EditableProject>) {
    onChange(items.map((item) => (item._key === key ? { ...item, ...patch } : item)));
  }

  function removeRow(key: string) {
    onChange(items.filter((item) => item._key !== key));
  }

  return (
    <div className="space-y-4">
      {items.length === 0 && (
        <EmptyState title="No projects added yet" description="Personal, academic, or team projects all count." />
      )}
      {items.map((item) => (
        <div key={item._key} className="relative rounded-[var(--radius-md)] border border-[var(--color-border)] p-4">
          <button
            type="button"
            onClick={() => removeRow(item._key)}
            aria-label="Remove project entry"
            className="absolute right-3 top-3 flex size-7 items-center justify-center rounded-[var(--radius-sm)] text-[var(--color-text-tertiary)] hover:bg-[var(--color-danger-subtle)] hover:text-[var(--color-danger)]"
          >
            <Trash2 className="size-4" aria-hidden />
          </button>
          <div className="grid gap-4 pr-8 sm:grid-cols-2">
            <div>
              <Label htmlFor={`proj-name-${item._key}`}>Project name</Label>
              <Input
                id={`proj-name-${item._key}`}
                value={item.name}
                onChange={(e) => updateRow(item._key, { name: e.target.value })}
                placeholder="Recommendation engine"
              />
            </div>
            <div>
              <Label htmlFor={`proj-role-${item._key}`}>Your role</Label>
              <Input
                id={`proj-role-${item._key}`}
                value={item.role ?? ""}
                onChange={(e) => updateRow(item._key, { role: e.target.value })}
                placeholder="Lead developer"
              />
            </div>
          </div>
          <div className="mt-4">
            <Label htmlFor={`proj-desc-${item._key}`}>Description</Label>
            <Textarea
              id={`proj-desc-${item._key}`}
              value={item.description ?? ""}
              onChange={(e) => updateRow(item._key, { description: e.target.value })}
              placeholder="What problem did it solve?"
            />
          </div>
          <div className="mt-4">
            <Label htmlFor={`proj-tech-${item._key}`}>Technologies</Label>
            <TagInput
              id={`proj-tech-${item._key}`}
              values={item.technologies}
              onChange={(values) => updateRow(item._key, { technologies: values })}
              placeholder="Add a technology"
            />
          </div>
          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            <div>
              <Label htmlFor={`proj-github-${item._key}`}>GitHub URL</Label>
              <Input
                id={`proj-github-${item._key}`}
                value={item.github_url ?? ""}
                onChange={(e) => updateRow(item._key, { github_url: e.target.value })}
                placeholder="https://github.com/..."
              />
            </div>
            <div>
              <Label htmlFor={`proj-url-${item._key}`}>Project URL</Label>
              <Input
                id={`proj-url-${item._key}`}
                value={item.project_url ?? ""}
                onChange={(e) => updateRow(item._key, { project_url: e.target.value })}
                placeholder="https://..."
              />
            </div>
            <div>
              <Label htmlFor={`proj-duration-${item._key}`}>Duration</Label>
              <Input
                id={`proj-duration-${item._key}`}
                value={item.duration ?? ""}
                onChange={(e) => updateRow(item._key, { duration: e.target.value })}
                placeholder="3 months"
              />
            </div>
          </div>
        </div>
      ))}
      <Button type="button" variant="outline" size="sm" onClick={() => onChange([...items, newProjectRow()])}>
        <Plus className="size-4" aria-hidden />
        Add project
      </Button>
    </div>
  );
}
