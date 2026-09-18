"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import useSWR from "swr";
import { Bookmark, BookmarkCheck } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { SavedJobOut } from "@/lib/types";

export function JobSaveButton({ jobId }: { jobId: string }) {
  const { user } = useAuth();
  const router = useRouter();
  const { data: savedJobs, mutate } = useSWR<SavedJobOut[]>(user ? "/saved-jobs" : null);
  const [pending, setPending] = useState(false);

  const isSaved = (savedJobs ?? []).some((s) => s.job.id === jobId);

  async function handleClick() {
    if (!user) {
      toast("Log in to save jobs", {
        description: "Create a free account to keep track of jobs you're interested in.",
        action: { label: "Log in", onClick: () => router.push("/login") },
      });
      return;
    }
    setPending(true);
    try {
      if (isSaved) {
        await api.delete(`/jobs/${jobId}/save`);
      } else {
        await api.post(`/jobs/${jobId}/save`);
      }
      await mutate();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't update saved jobs. Please try again.");
    } finally {
      setPending(false);
    }
  }

  return (
    <Button
      type="button"
      variant={isSaved ? "secondary" : "outline"}
      size="md"
      onClick={handleClick}
      isLoading={pending}
      className="shrink-0"
    >
      {isSaved ? <BookmarkCheck className="size-4" aria-hidden /> : <Bookmark className="size-4" aria-hidden />}
      {isSaved ? "Saved" : "Save job"}
    </Button>
  );
}
