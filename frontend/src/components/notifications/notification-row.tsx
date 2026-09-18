"use client";

import Link from "next/link";
import { Bell, Info, Mail, RefreshCw, Sparkles, TrendingUp } from "lucide-react";
import { formatRelativeTime, cn } from "@/lib/utils";
import type { NotificationOut, NotificationType } from "@/lib/types";

const NOTIFICATION_ICONS: Record<NotificationType, typeof Bell> = {
  NEW_MATCH: Sparkles,
  JOB_BECAME_MATCH: TrendingUp,
  JOB_STATUS_CHANGED: RefreshCw,
  DIGEST: Mail,
  SYSTEM: Info,
};

export function NotificationRow({
  notification,
  onOpen,
}: {
  notification: NotificationOut;
  onOpen: (notification: NotificationOut) => void;
}) {
  const Icon = NOTIFICATION_ICONS[notification.type] ?? Bell;
  const isUnread = !notification.is_read;
  const reason = notification.body || notification.reason_summary;

  const inner = (
    <div
      className={cn(
        "flex items-start gap-3.5 px-5 py-4 transition-colors",
        isUnread ? "bg-[var(--color-accent-subtle)]/40" : "hover:bg-[var(--color-bg-subtle)]"
      )}
    >
      <div className="relative flex shrink-0 items-center gap-3">
        {isUnread && (
          <span
            className="absolute -left-2.5 top-1/2 size-1.5 -translate-y-1/2 rounded-full bg-[var(--color-accent)]"
            aria-hidden
          />
        )}
        <div
          className={cn(
            "flex size-9 items-center justify-center rounded-[var(--radius-sm)]",
            isUnread ? "bg-[var(--color-accent-subtle)] text-[var(--color-accent)]" : "bg-[var(--color-bg-subtle)] text-[var(--color-text-secondary)]"
          )}
        >
          <Icon className="size-4" aria-hidden />
        </div>
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-start justify-between gap-3">
          <p
            className={cn(
              "text-[13.5px]",
              isUnread ? "font-semibold text-[var(--color-text-primary)]" : "font-medium text-[var(--color-text-primary)]"
            )}
          >
            {notification.title}
          </p>
          <span className="shrink-0 whitespace-nowrap pt-0.5 text-[12px] text-[var(--color-text-tertiary)]">
            {formatRelativeTime(notification.sent_at)}
          </span>
        </div>
        {reason && <p className="mt-1 text-[13px] leading-relaxed text-[var(--color-text-secondary)]">{reason}</p>}
      </div>
    </div>
  );

  return (
    <li className="border-b border-[var(--color-border)] last:border-b-0">
      {notification.job_id ? (
        <Link href={`/jobs/${notification.job_id}`} onClick={() => onOpen(notification)} className="block">
          {inner}
        </Link>
      ) : (
        <button type="button" onClick={() => onOpen(notification)} className="block w-full text-left">
          {inner}
        </button>
      )}
    </li>
  );
}
