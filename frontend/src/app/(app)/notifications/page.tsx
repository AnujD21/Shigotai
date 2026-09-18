"use client";

import useSWR, { mutate as globalMutate } from "swr";
import { BellRing, CheckCheck } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState, ErrorState } from "@/components/ui/state-views";
import { Button } from "@/components/ui/button";
import { NotificationRow } from "@/components/notifications/notification-row";
import { api, ApiError } from "@/lib/api";
import type { NotificationOut } from "@/lib/types";
import { toast } from "sonner";

interface NotificationListResponse {
  items: NotificationOut[];
  unread_count: number;
}

const NOTIFICATIONS_KEY = "/notifications?limit=50";
const BADGE_KEY = "/notifications?limit=5";

export default function NotificationsPage() {
  const { data, error, isLoading, mutate } = useSWR<NotificationListResponse>(NOTIFICATIONS_KEY);

  async function markRead(notification: NotificationOut) {
    if (notification.is_read) return;
    // Optimistic update
    mutate(
      (current) =>
        current && {
          items: current.items.map((n) => (n.id === notification.id ? { ...n, is_read: true } : n)),
          unread_count: Math.max(0, current.unread_count - 1),
        },
      { revalidate: false }
    );
    try {
      await api.put(`/notifications/${notification.id}/read`);
      globalMutate(BADGE_KEY);
    } catch (err) {
      mutate();
      toast.error(err instanceof ApiError ? err.message : "Couldn't mark that as read.");
    }
  }

  async function markAllRead() {
    if (!data || data.unread_count === 0) return;
    const previous = data;
    mutate(
      (current) => current && { items: current.items.map((n) => ({ ...n, is_read: true })), unread_count: 0 },
      { revalidate: false }
    );
    try {
      await api.put("/notifications/read-all");
      globalMutate(BADGE_KEY);
      toast.success("All caught up.");
    } catch (err) {
      mutate(previous, { revalidate: false });
      toast.error(err instanceof ApiError ? err.message : "Couldn't mark all as read.");
    }
  }

  const hasUnread = (data?.unread_count ?? 0) > 0;

  return (
    <>
      <PageHeader
        title="Notifications"
        description="Alerts about new matches, status changes, and digests -- with the reason behind each one."
        action={
          <Button variant="outline" size="sm" onClick={markAllRead} disabled={!hasUnread}>
            <CheckCheck className="size-3.5" aria-hidden />
            Mark all as read
          </Button>
        }
      />

      {error && (
        <ErrorState description="We couldn't load your notifications. Please try again." onRetry={() => mutate()} />
      )}

      {!error && isLoading && <NotificationsSkeleton />}

      {!error && !isLoading && data && data.items.length === 0 && (
        <EmptyState
          icon={BellRing}
          title="No alerts yet"
          description="We'll notify you here (and by email, if enabled) when a strong match appears."
        />
      )}

      {!error && !isLoading && data && data.items.length > 0 && (
        <Card className="overflow-hidden p-0">
          <ul>
            {data.items.map((notification) => (
              <NotificationRow key={notification.id} notification={notification} onOpen={markRead} />
            ))}
          </ul>
        </Card>
      )}
    </>
  );
}

function NotificationsSkeleton() {
  return (
    <Card className="overflow-hidden p-0">
      <ul>
        {Array.from({ length: 6 }).map((_, i) => (
          <li key={i} className="flex items-start gap-3.5 border-b border-[var(--color-border)] px-5 py-4 last:border-b-0">
            <Skeleton className="size-9 shrink-0 rounded-[var(--radius-sm)]" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-1/3" />
              <Skeleton className="h-3.5 w-2/3" />
            </div>
          </li>
        ))}
      </ul>
    </Card>
  );
}
