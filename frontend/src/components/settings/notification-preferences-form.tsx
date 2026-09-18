"use client";

import { useEffect, useState } from "react";
import { Bell } from "lucide-react";
import { toast } from "sonner";
import useSWR from "swr";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { FieldHint, Label, Select } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorState } from "@/components/ui/state-views";
import { Button } from "@/components/ui/button";
import { api, ApiError } from "@/lib/api";
import type { NotificationFrequency, NotificationPreferenceOut } from "@/lib/types";

const FREQUENCY_OPTIONS: { value: NotificationFrequency; label: string }[] = [
  { value: "INSTANT", label: "Instant" },
  { value: "DAILY_DIGEST", label: "Daily digest" },
  { value: "WEEKLY_DIGEST", label: "Weekly digest" },
  { value: "OFF", label: "Off" },
];

const MAX_PER_DAY_OPTIONS = [1, 3, 5, 10, 20];

export function NotificationPreferencesForm() {
  const { data, error, isLoading, mutate } = useSWR<NotificationPreferenceOut>("/notification-preferences");
  const [form, setForm] = useState<NotificationPreferenceOut | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    // Seed local editable form state from the fetched preferences exactly
    // once (SWR data arrives async after mount) -- a sanctioned data-sync
    // exception to this rule, not a value derivable during render.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (data && !form) setForm(data);
  }, [data, form]);

  if (error) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center gap-2.5">
          <Bell className="size-4 text-[var(--color-text-secondary)]" aria-hidden />
          <CardTitle>Notification preferences</CardTitle>
        </CardHeader>
        <CardContent>
          <ErrorState
            description="We couldn't load your notification preferences. Please try again."
            onRetry={() => mutate()}
          />
        </CardContent>
      </Card>
    );
  }

  if (isLoading || !form) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center gap-2.5">
          <Bell className="size-4 text-[var(--color-text-secondary)]" aria-hidden />
          <CardTitle>Notification preferences</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          <Skeleton className="h-9 w-full" />
          <Skeleton className="h-5 w-2/3" />
          <Skeleton className="h-5 w-1/2" />
          <Skeleton className="h-9 w-full" />
          <Skeleton className="h-9 w-1/2" />
        </CardContent>
      </Card>
    );
  }

  function update<K extends keyof NotificationPreferenceOut>(key: K, value: NotificationPreferenceOut[K]) {
    setForm((current) => current && { ...current, [key]: value });
  }

  async function handleSave() {
    if (!form) return;
    setIsSaving(true);
    try {
      const saved = await api.put<NotificationPreferenceOut>("/notification-preferences", form);
      setForm(saved);
      mutate(saved, { revalidate: false });
      toast.success("Preferences saved.");
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't save preferences. Please try again.");
    } finally {
      setIsSaving(false);
    }
  }

  const thresholdPercent = Math.round(form.min_match_threshold * 100);

  return (
    <Card>
      <CardHeader className="flex flex-row items-center gap-2.5">
        <Bell className="size-4 text-[var(--color-text-secondary)]" aria-hidden />
        <CardTitle>Notification preferences</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <Label htmlFor="frequency">Frequency</Label>
          <Select
            id="frequency"
            value={form.frequency}
            onChange={(e) => update("frequency", e.target.value as NotificationFrequency)}
          >
            {FREQUENCY_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </Select>
          <FieldHint>How often Shigotai sends you alerts about new matches and job changes.</FieldHint>
        </div>

        <div className="space-y-3.5 border-t border-[var(--color-border)] pt-5">
          <Checkbox
            label="Email notifications"
            description="Receive alerts by email in addition to your in-app feed."
            checked={form.email_enabled}
            onChange={(e) => update("email_enabled", e.target.checked)}
          />
          <Checkbox
            label="Browser push (not available in this demo environment)"
            description="Push notifications require a browser subscription flow that isn't wired up in this demo backend."
            checked={false}
            disabled
            title="Browser push isn't available in this demo environment."
          />
        </div>

        <div className="border-t border-[var(--color-border)] pt-5">
          <Label htmlFor="threshold">Minimum match strength to notify me: {thresholdPercent}%</Label>
          <input
            id="threshold"
            type="range"
            min={0}
            max={100}
            step={5}
            value={thresholdPercent}
            onChange={(e) => update("min_match_threshold", Number(e.target.value) / 100)}
            className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-[var(--color-border-strong)] accent-[var(--color-accent)]"
          />
          <div className="mt-1 flex justify-between text-[11.5px] text-[var(--color-text-tertiary)]">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
          <FieldHint>Only send alerts for jobs matching at least this percentage.</FieldHint>
        </div>

        <div className="border-t border-[var(--color-border)] pt-5">
          <Label htmlFor="max-per-day">Maximum notifications per day</Label>
          <Select
            id="max-per-day"
            value={
              MAX_PER_DAY_OPTIONS.includes(form.max_notifications_per_day)
                ? String(form.max_notifications_per_day)
                : "custom"
            }
            onChange={(e) => update("max_notifications_per_day", Number(e.target.value))}
          >
            {!MAX_PER_DAY_OPTIONS.includes(form.max_notifications_per_day) && (
              <option value="custom">{form.max_notifications_per_day} (current)</option>
            )}
            {MAX_PER_DAY_OPTIONS.map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </Select>
          <FieldHint>Caps how many alerts you&apos;ll receive in a single day.</FieldHint>
        </div>

        <div className="space-y-3.5 border-t border-[var(--color-border)] pt-5">
          <Checkbox
            label="Notify me about new graduate roles"
            checked={form.notify_new_graduate}
            onChange={(e) => update("notify_new_graduate", e.target.checked)}
          />
          <Checkbox
            label="Notify me about visa-sponsorship-related roles"
            checked={form.notify_visa_related}
            onChange={(e) => update("notify_visa_related", e.target.checked)}
          />
          <Checkbox
            label="Only notify me about high-match roles"
            checked={form.notify_high_match_only}
            onChange={(e) => update("notify_high_match_only", e.target.checked)}
          />
        </div>

        <div className="flex justify-end border-t border-[var(--color-border)] pt-5">
          <Button variant="accent" onClick={handleSave} isLoading={isSaving}>
            Save preferences
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
