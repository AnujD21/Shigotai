"use client";

import { Suspense, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { AuthCard } from "@/components/auth/auth-card";
import { Button } from "@/components/ui/button";
import { FieldError, Input, Label } from "@/components/ui/input";
import { api, ApiError } from "@/lib/api";

const schema = z.object({ password: z.string().min(8, "Use at least 8 characters.") });
type FormValues = z.infer<typeof schema>;

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [serverError, setServerError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    if (!token) {
      setServerError("This reset link is missing its token. Please request a new one.");
      return;
    }
    setServerError(null);
    try {
      await api.post("/auth/password-reset/confirm", { token, new_password: values.password }, { auth: false });
      toast.success("Password updated. Please log in.");
      router.push("/login");
    } catch (error) {
      setServerError(error instanceof ApiError ? error.message : "This link may have expired. Please request a new one.");
    }
  }

  return (
    <AuthCard title="Set a new password">
      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
        <div>
          <Label htmlFor="password">New password</Label>
          <Input id="password" type="password" autoComplete="new-password" invalid={!!errors.password} {...register("password")} />
          <FieldError>{errors.password?.message}</FieldError>
        </div>
        {serverError && (
          <p role="alert" className="rounded-[var(--radius-sm)] bg-[var(--color-danger-subtle)] px-3 py-2.5 text-[13px] text-[var(--color-danger)]">
            {serverError}
          </p>
        )}
        <Button type="submit" variant="accent" size="lg" className="w-full" isLoading={isSubmitting}>
          Update password
        </Button>
      </form>
      <p className="mt-6 text-center text-[13.5px] text-[var(--color-text-secondary)]">
        <Link href="/login" className="font-medium text-[var(--color-accent)]">
          Back to log in
        </Link>
      </p>
    </AuthCard>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense>
      <ResetPasswordForm />
    </Suspense>
  );
}
