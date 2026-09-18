"use client";

import { useRef, useState } from "react";
import { Loader2, UploadCloud } from "lucide-react";
import { toast } from "sonner";
import { api, ApiError } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ResumeReviewDialog, type AcceptedResumeItems } from "@/components/profile/resume-review-dialog";
import type { ResumeExtractionResult } from "@/lib/types";
import { cn } from "@/lib/utils";

const MAX_SIZE_BYTES = 5 * 1024 * 1024;
const ACCEPTED_EXTENSIONS = [".pdf", ".docx"];

export function ResumeUploadCard({
  currentFilename,
  onAccept,
}: {
  currentFilename?: string | null;
  onAccept: (accepted: AcceptedResumeItems) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [result, setResult] = useState<ResumeExtractionResult | null>(null);

  function validate(file: File): string | null {
    const lower = file.name.toLowerCase();
    if (!ACCEPTED_EXTENSIONS.some((ext) => lower.endsWith(ext))) {
      return "Please upload a .pdf or .docx file.";
    }
    if (file.size > MAX_SIZE_BYTES) {
      return "That file is too large. Maximum size is 5MB.";
    }
    return null;
  }

  async function handleFile(file: File) {
    const validationError = validate(file);
    if (validationError) {
      toast.error(validationError);
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    setIsUploading(true);
    try {
      const extraction = await api.upload<ResumeExtractionResult>("/resume/upload", formData);
      setResult(extraction);
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Couldn't analyze that resume. Please try again.");
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle as="h2">Resume</CardTitle>
      </CardHeader>
      <CardContent>
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(e) => {
            e.preventDefault();
            setIsDragging(false);
            const file = e.dataTransfer.files?.[0];
            if (file) handleFile(file);
          }}
          className={cn(
            "flex flex-col items-center justify-center gap-3 rounded-[var(--radius-md)] border border-dashed px-6 py-10 text-center transition-colors",
            isDragging
              ? "border-[var(--color-accent)] bg-[var(--color-accent-subtle)]"
              : "border-[var(--color-border-strong)]"
          )}
        >
          {isUploading ? (
            <>
              <Loader2 className="size-6 animate-spin text-[var(--color-accent)]" aria-hidden />
              <p className="text-[13.5px] font-medium text-[var(--color-text-primary)]">Analyzing your resume...</p>
            </>
          ) : (
            <>
              <UploadCloud className="size-6 text-[var(--color-text-tertiary)]" aria-hidden />
              <div>
                <p className="text-[13.5px] font-medium text-[var(--color-text-primary)]">
                  Drag &amp; drop your resume, or{" "}
                  <button
                    type="button"
                    onClick={() => inputRef.current?.click()}
                    className="text-[var(--color-accent)] underline underline-offset-2"
                  >
                    browse
                  </button>
                </p>
                <p className="mt-1 text-[12.5px] text-[var(--color-text-tertiary)]">PDF or DOCX, up to 5MB.</p>
                {currentFilename && (
                  <p className="mt-1 text-[12.5px] text-[var(--color-text-tertiary)]">
                    Current file on record: {currentFilename}
                  </p>
                )}
              </div>
            </>
          )}
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.docx"
            className="hidden"
            aria-label="Upload resume file"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFile(file);
              e.target.value = "";
            }}
          />
        </div>
      </CardContent>

      <ResumeReviewDialog
        result={result}
        onClose={() => setResult(null)}
        onConfirm={(accepted) => {
          onAccept(accepted);
          setResult(null);
          toast.success("Added the selected items. Don't forget to save your profile.");
        }}
      />
    </Card>
  );
}
