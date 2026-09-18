"use client";

import { Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input, Label } from "@/components/ui/input";
import { EmptyState } from "@/components/ui/state-views";
import type { CertificationEntry } from "@/lib/types";

export type EditableCertification = CertificationEntry & { _key: string };

export function newCertificationRow(): EditableCertification {
  return {
    _key: crypto.randomUUID(),
    name: "",
    issuer: "",
    year: null,
  };
}

export function CertificationsSection({
  items,
  onChange,
}: {
  items: EditableCertification[];
  onChange: (items: EditableCertification[]) => void;
}) {
  function updateRow(key: string, patch: Partial<EditableCertification>) {
    onChange(items.map((item) => (item._key === key ? { ...item, ...patch } : item)));
  }

  function removeRow(key: string) {
    onChange(items.filter((item) => item._key !== key));
  }

  return (
    <div className="space-y-4">
      {items.length === 0 && (
        <EmptyState title="No certifications added yet" description="JLPT, cloud certs, or other credentials." />
      )}
      {items.map((item) => (
        <div key={item._key} className="relative rounded-[var(--radius-md)] border border-[var(--color-border)] p-4">
          <button
            type="button"
            onClick={() => removeRow(item._key)}
            aria-label="Remove certification entry"
            className="absolute right-3 top-3 flex size-7 items-center justify-center rounded-[var(--radius-sm)] text-[var(--color-text-tertiary)] hover:bg-[var(--color-danger-subtle)] hover:text-[var(--color-danger)]"
          >
            <Trash2 className="size-4" aria-hidden />
          </button>
          <div className="grid gap-4 pr-8 sm:grid-cols-3">
            <div>
              <Label htmlFor={`cert-name-${item._key}`}>Certification name</Label>
              <Input
                id={`cert-name-${item._key}`}
                value={item.name}
                onChange={(e) => updateRow(item._key, { name: e.target.value })}
                placeholder="AWS Certified Developer"
              />
            </div>
            <div>
              <Label htmlFor={`cert-issuer-${item._key}`}>Issuer</Label>
              <Input
                id={`cert-issuer-${item._key}`}
                value={item.issuer ?? ""}
                onChange={(e) => updateRow(item._key, { issuer: e.target.value })}
                placeholder="Amazon Web Services"
              />
            </div>
            <div>
              <Label htmlFor={`cert-year-${item._key}`}>Year</Label>
              <Input
                id={`cert-year-${item._key}`}
                type="number"
                inputMode="numeric"
                value={item.year ?? ""}
                onChange={(e) => updateRow(item._key, { year: e.target.value ? Number(e.target.value) : null })}
                placeholder="2024"
              />
            </div>
          </div>
        </div>
      ))}
      <Button type="button" variant="outline" size="sm" onClick={() => onChange([...items, newCertificationRow()])}>
        <Plus className="size-4" aria-hidden />
        Add certification
      </Button>
    </div>
  );
}
