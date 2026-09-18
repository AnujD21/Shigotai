"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import { Logo } from "@/components/ui/logo";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { LinkButton } from "@/components/ui/link-button";
import { useAuth } from "@/lib/auth-context";
import { cn } from "@/lib/utils";

const LINKS = [
  { href: "/jobs", label: "Explore Jobs" },
  { href: "/companies", label: "Companies" },
  { href: "/how-it-works", label: "How it works" },
];

export function PublicNavbar() {
  const pathname = usePathname();
  const { user, isLoading } = useAuth();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-[var(--color-border)] bg-[var(--color-bg)]/85 backdrop-blur-sm">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5 md:px-8">
        <Logo />

        <nav className="hidden items-center gap-7 md:flex">
          {LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "text-[13.5px] font-medium text-[var(--color-text-secondary)] transition-colors hover:text-[var(--color-text-primary)]",
                pathname.startsWith(link.href) && "text-[var(--color-text-primary)]"
              )}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          <ThemeToggle />
          {!isLoading && user ? (
            <LinkButton href="/dashboard" variant="secondary" size="sm">
              Dashboard
            </LinkButton>
          ) : (
            <>
              <LinkButton href="/login" variant="ghost" size="sm">
                Log in
              </LinkButton>
              <LinkButton href="/register" variant="accent" size="sm">
                Build My Profile
              </LinkButton>
            </>
          )}
        </div>

        <button
          type="button"
          className="flex size-9 items-center justify-center rounded-[var(--radius-sm)] text-[var(--color-text-primary)] md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label={open ? "Close menu" : "Open menu"}
          aria-expanded={open}
        >
          {open ? <X className="size-5" /> : <Menu className="size-5" />}
        </button>
      </div>

      {open && (
        <div className="border-t border-[var(--color-border)] px-5 py-4 md:hidden">
          <nav className="flex flex-col gap-1">
            {LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setOpen(false)}
                className="rounded-[var(--radius-sm)] px-2 py-2.5 text-[14px] font-medium text-[var(--color-text-primary)] hover:bg-[var(--color-bg-subtle)]"
              >
                {link.label}
              </Link>
            ))}
          </nav>
          <div className="mt-3 flex items-center gap-2 border-t border-[var(--color-border)] pt-3">
            <ThemeToggle />
            {!isLoading && user ? (
              <LinkButton href="/dashboard" variant="secondary" size="sm" className="flex-1">
                Dashboard
              </LinkButton>
            ) : (
              <>
                <LinkButton href="/login" variant="ghost" size="sm" className="flex-1">
                  Log in
                </LinkButton>
                <LinkButton href="/register" variant="accent" size="sm" className="flex-1">
                  Sign up
                </LinkButton>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
