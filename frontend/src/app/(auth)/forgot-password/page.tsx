"use client";

import { useState } from "react";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { CheckCircle2 } from "lucide-react";
import { AuthCard } from "@/components/auth/auth-card";
import { Button } from "@/components/ui/button";
import { FieldError, Input, Label } from "@/components/ui/input";
import { api } from "@/lib/api";

const schema = z.object({ email: z.string().email("Enter a valid email address.") });
type FormValues = z.infer<typeof schema>;

export default function ForgotPasswordPage() {
  const [sent, setSent] = useState(false);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    await api.post("/auth/password-reset/request", { email: values.email }, { auth: false });
    setSent(true);
  }

  if (sent) {
    return (
      <AuthCard title="Check your email">
        <div className="flex flex-col items-center py-2 text-center">
          <div className="flex size-11 items-center justify-center rounded-full bg-[var(--color-success-subtle)]">
            <CheckCircle2 className="size-5 text-[var(--color-success)]" aria-hidden />
          </div>
          <p className="mt-4 text-[13.5px] leading-relaxed text-[var(--color-text-secondary)]">
            If an account exists for that email, we&apos;ve sent a link to reset your password.
          </p>
          <Link href="/login" className="mt-5 text-[13.5px] font-medium text-[var(--color-accent)]">
            Back to log in
          </Link>
        </div>
      </AuthCard>
    );
  }

  return (
    <AuthCard title="Reset your password" description="We'll email you a link to get back in.">
      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
        <div>
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" autoComplete="email" invalid={!!errors.email} {...register("email")} />
          <FieldError>{errors.email?.message}</FieldError>
        </div>
        <Button type="submit" variant="accent" size="lg" className="w-full" isLoading={isSubmitting}>
          Send reset link
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
