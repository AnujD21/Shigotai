"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { CheckCircle2, Loader2, XCircle } from "lucide-react";
import { AuthCard } from "@/components/auth/auth-card";
import { api, ApiError } from "@/lib/api";

function VerifyEmailContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    // One-time verification call driven by the URL token, not a value derivable
    // during render -- the sanctioned data-fetching exception to this rule.
    if (!token) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setStatus("error");
      setMessage("This verification link is missing its token.");
      return;
    }
    api
      .post("/auth/verify-email", { token }, { auth: false })
      .then(() => setStatus("success"))
      .catch((error) => {
        setStatus("error");
        setMessage(error instanceof ApiError ? error.message : "This link may have expired.");
      });
  }, [token]);

  return (
    <AuthCard title="Email verification">
      <div className="flex flex-col items-center py-2 text-center">
        {status === "loading" && (
          <>
            <Loader2 className="size-6 animate-spin text-[var(--color-text-tertiary)]" aria-hidden />
            <p className="mt-4 text-[13.5px] text-[var(--color-text-secondary)]">Verifying your email...</p>
          </>
        )}
        {status === "success" && (
          <>
            <div className="flex size-11 items-center justify-center rounded-full bg-[var(--color-success-subtle)]">
              <CheckCircle2 className="size-5 text-[var(--color-success)]" aria-hidden />
            </div>
            <p className="mt-4 text-[13.5px] text-[var(--color-text-secondary)]">Your email is verified.</p>
            <Link href="/dashboard" className="mt-5 text-[13.5px] font-medium text-[var(--color-accent)]">
              Go to dashboard
            </Link>
          </>
        )}
        {status === "error" && (
          <>
            <div className="flex size-11 items-center justify-center rounded-full bg-[var(--color-danger-subtle)]">
              <XCircle className="size-5 text-[var(--color-danger)]" aria-hidden />
            </div>
            <p className="mt-4 text-[13.5px] text-[var(--color-text-secondary)]">{message}</p>
            <Link href="/login" className="mt-5 text-[13.5px] font-medium text-[var(--color-accent)]">
              Back to log in
            </Link>
          </>
        )}
      </div>
    </AuthCard>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense>
      <VerifyEmailContent />
    </Suspense>
  );
}
