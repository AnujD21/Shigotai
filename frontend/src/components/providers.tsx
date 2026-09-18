"use client";

import { ThemeProvider } from "next-themes";
import { SWRConfig } from "swr";
import { Toaster } from "sonner";
import { AuthProvider } from "@/lib/auth-context";
import { api } from "@/lib/api";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="data-theme" defaultTheme="system" enableSystem disableTransitionOnChange>
      <AuthProvider>
        <SWRConfig value={{ fetcher: (url: string) => api.get(url), revalidateOnFocus: false }}>
          {children}
        </SWRConfig>
        <Toaster
          position="bottom-right"
          toastOptions={{
            style: {
              background: "var(--color-surface)",
              color: "var(--color-text-primary)",
              border: "1px solid var(--color-border)",
              borderRadius: "10px",
              fontSize: "13.5px",
            },
          }}
        />
      </AuthProvider>
    </ThemeProvider>
  );
}
