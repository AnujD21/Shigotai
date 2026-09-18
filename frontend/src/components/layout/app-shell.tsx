"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Bell,
  Bookmark,
  LayoutDashboard,
  LogOut,
  Menu,
  Settings,
  Sparkles,
  Search,
  User as UserIcon,
  X,
} from "lucide-react";
import useSWR from "swr";
import { Logo } from "@/components/ui/logo";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { ErrorState } from "@/components/ui/state-views";
import { useAuth } from "@/lib/auth-context";
import { cn } from "@/lib/utils";
import type { NotificationOut } from "@/lib/types";

interface NotificationListResponse {
  items: NotificationOut[];
  unread_count: number;
}

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", mobileLabel: "Dashboard", icon: LayoutDashboard },
  { href: "/matches", label: "My Matches", mobileLabel: "Matches", icon: Sparkles },
  { href: "/jobs", label: "Discover Jobs", mobileLabel: "Discover", icon: Search },
  { href: "/saved", label: "Saved Jobs", mobileLabel: "Saved", icon: Bookmark },
  { href: "/notifications", label: "Notifications", mobileLabel: "Alerts", icon: Bell },
  { href: "/profile", label: "My Profile", mobileLabel: "Profile", icon: UserIcon },
  { href: "/settings", label: "Settings", mobileLabel: "Settings", icon: Settings },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isLoading, authError, logout, refreshUser } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);

  const { data } = useSWR<NotificationListResponse>(user ? "/notifications?limit=5" : null);
  const unreadCount = data?.unread_count ?? 0;

  useEffect(() => {
    if (!isLoading && !user && !authError) {
      router.replace(`/login?next=${encodeURIComponent(pathname)}`);
    }
  }, [isLoading, user, authError, router, pathname]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg)]">
        <div className="size-6 animate-spin rounded-full border-2 border-[var(--color-border-strong)] border-t-[var(--color-accent)]" />
      </div>
    );
  }

  if (authError && !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg)] p-6">
        <div className="w-full max-w-sm">
          <ErrorState
            title="Can't reach Shigotai"
            description="We couldn't verify your session. Check your connection and try again."
            onRetry={refreshUser}
          />
        </div>
      </div>
    );
  }

  if (!user) return null;

  return (
    <div className="min-h-screen bg-[var(--color-bg)] md:flex">
      {/* Desktop sidebar */}
      <aside className="hidden w-60 shrink-0 flex-col border-r border-[var(--color-border)] px-4 py-6 md:flex">
        <div className="px-2">
          <Logo />
        </div>
        <nav className="mt-8 flex-1 space-y-1">
          {NAV_ITEMS.map((item) => {
            const active = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-2.5 rounded-[var(--radius-sm)] px-3 py-2.5 text-[13.5px] font-medium text-[var(--color-text-secondary)] transition-colors hover:bg-[var(--color-bg-subtle)] hover:text-[var(--color-text-primary)]",
                  active && "bg-[var(--color-bg-subtle)] text-[var(--color-text-primary)]"
                )}
              >
                <item.icon className="size-4" aria-hidden />
                {item.label}
                {item.href === "/notifications" && unreadCount > 0 && (
                  <span className="ml-auto flex size-5 items-center justify-center rounded-full bg-[var(--color-accent)] text-[10px] font-semibold text-[var(--color-text-on-accent)]">
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>
        <div className="space-y-3 border-t border-[var(--color-border)] pt-4">
          <div className="flex items-center justify-between px-2">
            <div className="min-w-0">
              <p className="truncate text-[13px] font-medium text-[var(--color-text-primary)]">{user.full_name}</p>
              <p className="truncate text-[12px] text-[var(--color-text-tertiary)]">{user.email}</p>
            </div>
            <ThemeToggle />
          </div>
          <button
            type="button"
            onClick={() => {
              logout();
              router.push("/");
            }}
            className="flex w-full items-center gap-2.5 rounded-[var(--radius-sm)] px-3 py-2 text-[13px] font-medium text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-subtle)] hover:text-[var(--color-danger)]"
          >
            <LogOut className="size-4" aria-hidden />
            Log out
          </button>
        </div>
      </aside>

      {/* Mobile top bar */}
      <header className="sticky top-0 z-30 flex items-center justify-between border-b border-[var(--color-border)] bg-[var(--color-bg)]/90 px-4 py-3 backdrop-blur-sm md:hidden">
        <Logo />
        <div className="flex items-center gap-1">
          <Link
            href="/notifications"
            className="relative flex size-9 items-center justify-center rounded-[var(--radius-sm)] text-[var(--color-text-secondary)]"
            aria-label="Notifications"
          >
            <Bell className="size-[18px]" aria-hidden />
            {unreadCount > 0 && (
              <span className="absolute right-1.5 top-1.5 size-2 rounded-full bg-[var(--color-accent)]" />
            )}
          </Link>
          <button
            type="button"
            onClick={() => setMobileOpen(true)}
            className="flex size-9 items-center justify-center rounded-[var(--radius-sm)] text-[var(--color-text-primary)]"
            aria-label="Open menu"
          >
            <Menu className="size-5" aria-hidden />
          </button>
        </div>
      </header>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="absolute inset-0 bg-[var(--color-overlay)]" onClick={() => setMobileOpen(false)} />
          <div className="absolute right-0 top-0 h-full w-72 max-w-[80vw] bg-[var(--color-surface)] p-5 shadow-[var(--shadow-lg)]">
            <div className="flex items-center justify-between">
              <p className="text-[13px] font-medium text-[var(--color-text-primary)]">{user.full_name}</p>
              <button
                type="button"
                onClick={() => setMobileOpen(false)}
                aria-label="Close menu"
                className="flex size-8 items-center justify-center rounded-[var(--radius-sm)] text-[var(--color-text-secondary)]"
              >
                <X className="size-4.5" aria-hidden />
              </button>
            </div>
            <nav className="mt-6 space-y-1">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileOpen(false)}
                  className={cn(
                    "flex items-center gap-2.5 rounded-[var(--radius-sm)] px-3 py-2.5 text-[14px] font-medium text-[var(--color-text-secondary)]",
                    pathname.startsWith(item.href) && "bg-[var(--color-bg-subtle)] text-[var(--color-text-primary)]"
                  )}
                >
                  <item.icon className="size-4" aria-hidden />
                  {item.label}
                </Link>
              ))}
            </nav>
            <div className="mt-6 flex items-center justify-between border-t border-[var(--color-border)] pt-4">
              <ThemeToggle />
              <button
                type="button"
                onClick={() => {
                  logout();
                  router.push("/");
                }}
                className="flex items-center gap-2 text-[13px] font-medium text-[var(--color-danger)]"
              >
                <LogOut className="size-4" aria-hidden />
                Log out
              </button>
            </div>
          </div>
        </div>
      )}

      <main className="min-w-0 flex-1 pb-20 md:pb-0">
        <div className="mx-auto max-w-5xl px-4 py-6 md:px-8 md:py-10">{children}</div>
      </main>

      {/* Mobile bottom tab bar */}
      <nav className="fixed bottom-0 left-0 right-0 z-30 grid grid-cols-5 border-t border-[var(--color-border)] bg-[var(--color-bg)]/95 backdrop-blur-sm md:hidden">
        {NAV_ITEMS.slice(0, 5).map((item) => {
          const active = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex flex-col items-center gap-1 py-2.5 text-[10.5px] font-medium text-[var(--color-text-tertiary)]",
                active && "text-[var(--color-accent)]"
              )}
            >
              <item.icon className="size-[18px]" aria-hidden />
              {item.mobileLabel}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
