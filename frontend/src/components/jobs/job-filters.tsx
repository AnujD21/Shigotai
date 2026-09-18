"use client";

import { useEffect, useRef, useState } from "react";
import { Search } from "lucide-react";
import { Input, Select, Label } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";

export interface JobFilterValues {
  q: string;
  location: string;
  employment_type: string;
  work_mode: string;
  only_verified_active: boolean;
  new_graduate: boolean;
  visa_sponsorship: boolean;
  sort: string;
}

export const DEFAULT_JOB_FILTERS: JobFilterValues = {
  q: "",
  location: "",
  employment_type: "",
  work_mode: "",
  only_verified_active: false,
  new_graduate: false,
  visa_sponsorship: false,
  sort: "recently_verified",
};

export function JobFilters({
  values,
  onTextChange,
  onImmediateChange,
  onClear,
  hasActiveFilters,
}: {
  values: JobFilterValues;
  onTextChange: (patch: Partial<Pick<JobFilterValues, "q" | "location">>) => void;
  onImmediateChange: (patch: Partial<JobFilterValues>) => void;
  onClear: () => void;
  hasActiveFilters: boolean;
}) {
  // Local text state, initialized from the URL-derived values. The parent
  // remounts this component (via a `key` tied to values.q/values.location)
  // whenever those change externally -- e.g. "Clear filters" or browser
  // back/forward -- so no effect-based resync is needed here.
  const [q, setQ] = useState(values.q);
  const [location, setLocation] = useState(values.location);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      if (q !== values.q || location !== values.location) {
        onTextChange({ q, location });
      }
    }, 300);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q, location]);

  return (
    <div className="rounded-[var(--radius-lg)] border border-[var(--color-border)] bg-[var(--color-surface)] p-4 md:p-5">
      <div className="grid gap-3 md:grid-cols-[1.6fr_1fr]">
        <div className="relative">
          <Search
            className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-[var(--color-text-tertiary)]"
            aria-hidden
          />
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search job titles, skills, companies..."
            className="pl-10"
            aria-label="Search jobs"
          />
        </div>
        <Input
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          placeholder="Location (e.g. Tokyo)"
          aria-label="Location"
        />
      </div>

      <div className="mt-3 grid gap-3 sm:grid-cols-2 md:grid-cols-4">
        <div>
          <Label htmlFor="job-filter-employment-type">Employment type</Label>
          <Select
            id="job-filter-employment-type"
            value={values.employment_type}
            onChange={(e) => onImmediateChange({ employment_type: e.target.value })}
          >
            <option value="">Any</option>
            <option value="FULL_TIME">Full-time</option>
            <option value="INTERNSHIP">Internship</option>
            <option value="CONTRACT">Contract</option>
            <option value="NEW_GRADUATE">New graduate</option>
          </Select>
        </div>
        <div>
          <Label htmlFor="job-filter-work-mode">Work mode</Label>
          <Select
            id="job-filter-work-mode"
            value={values.work_mode}
            onChange={(e) => onImmediateChange({ work_mode: e.target.value })}
          >
            <option value="">Any</option>
            <option value="ONSITE">Onsite</option>
            <option value="HYBRID">Hybrid</option>
            <option value="REMOTE">Remote</option>
          </Select>
        </div>
        <div>
          <Label htmlFor="job-filter-sort">Sort by</Label>
          <Select
            id="job-filter-sort"
            value={values.sort}
            onChange={(e) => onImmediateChange({ sort: e.target.value })}
          >
            <option value="recently_verified">Recently verified</option>
            <option value="recently_posted">Recently posted</option>
            <option value="salary_desc">Salary (highest)</option>
          </Select>
        </div>
        <div className="flex items-end">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onClear}
            disabled={!hasActiveFilters}
            className="w-full sm:w-auto"
          >
            Clear filters
          </Button>
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 border-t border-[var(--color-border)] pt-4">
        <Checkbox
          label="Only verified active jobs"
          checked={values.only_verified_active}
          onChange={(e) => onImmediateChange({ only_verified_active: e.target.checked })}
        />
        <Checkbox
          label="New graduate eligible"
          checked={values.new_graduate}
          onChange={(e) => onImmediateChange({ new_graduate: e.target.checked })}
        />
        <Checkbox
          label="Visa sponsorship offered"
          checked={values.visa_sponsorship}
          onChange={(e) => onImmediateChange({ visa_sponsorship: e.target.checked })}
        />
      </div>
    </div>
  );
}
