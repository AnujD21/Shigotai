"use client";

import { KeyRound, Palette, UserRound } from "lucide-react";
import { PageHeader } from "@/components/ui/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { LinkButton } from "@/components/ui/link-button";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { NotificationPreferencesForm } from "@/components/settings/notification-preferences-form";
import { useAuth } from "@/lib/auth-context";

export default function SettingsPage() {
  const { user } = useAuth();

  return (
    <>
      <PageHeader title="Settings" description="Manage your account, appearance, and notification preferences." />

      <div className="space-y-6">
        <Card>
          <CardHeader className="flex flex-row items-center gap-2.5">
            <UserRound className="size-4 text-[var(--color-text-secondary)]" aria-hidden />
            <CardTitle as="h2">Account</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <p className="text-[12px] font-medium text-[var(--color-text-tertiary)]">Full name</p>
                <p className="mt-1 text-[14px] text-[var(--color-text-primary)]">{user?.full_name}</p>
              </div>
              <div>
                <p className="text-[12px] font-medium text-[var(--color-text-tertiary)]">Email</p>
                <div className="mt-1 flex items-center gap-2">
                  <p className="text-[14px] text-[var(--color-text-primary)]">{user?.email}</p>
                  <Badge tone={user?.is_email_verified ? "success" : "warning"}>
                    {user?.is_email_verified ? "Verified" : "Unverified"}
                  </Badge>
                </div>
              </div>
            </div>

            <p className="text-[12.5px] text-[var(--color-text-tertiary)]">
              Profile details -- education, skills, experience, and preferences -- are managed on your{" "}
              <a href="/profile" className="font-medium text-[var(--color-accent)]">
                Profile
              </a>{" "}
              page.
            </p>

            <div className="border-t border-[var(--color-border)] pt-5">
              <LinkButton href="/forgot-password" variant="outline" size="sm">
                <KeyRound className="size-3.5" aria-hidden />
                Change password
              </LinkButton>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center gap-2.5">
            <Palette className="size-4 text-[var(--color-text-secondary)]" aria-hidden />
            <CardTitle>Appearance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between gap-4">
              <p className="text-[13.5px] text-[var(--color-text-secondary)]">
                Shigotai follows your system preference by default. Switch it manually here.
              </p>
              <ThemeToggle />
            </div>
          </CardContent>
        </Card>

        <NotificationPreferencesForm />
      </div>
    </>
  );
}
