import { Logo } from "@/components/ui/logo";
import { ThemeToggle } from "@/components/ui/theme-toggle";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="grain relative flex min-h-screen flex-col overflow-hidden bg-[var(--color-bg-subtle)]">
      <div className="dot-grid pointer-events-none absolute inset-0 -z-10 opacity-50" aria-hidden />
      <div
        aria-hidden
        className="pointer-events-none absolute -top-48 left-1/2 -z-10 size-[560px] -translate-x-1/2 rounded-full bg-[radial-gradient(circle,color-mix(in_srgb,var(--color-accent)_16%,transparent),transparent_65%)] blur-2xl"
      />
      <header className="flex items-center justify-between px-5 py-5 md:px-8">
        <Logo />
        <ThemeToggle />
      </header>
      <main id="main-content" className="flex flex-1 items-center justify-center px-5 pb-16">
        <div className="w-full max-w-[420px]">{children}</div>
      </main>
    </div>
  );
}
