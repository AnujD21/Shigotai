"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { Check, FileText, Loader2, UploadCloud } from "lucide-react";
import { toast } from "sonner";
import { api, ApiError } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ResumeReviewDialog, type AcceptedResumeItems } from "@/components/profile/resume-review-dialog";
import type { ResumeExtractionResult } from "@/lib/types";
import { cn } from "@/lib/utils";

// Vercel caps request bodies at 4.5MB; the API enforces the same 4MB limit.
const MAX_SIZE_BYTES = 4 * 1024 * 1024;
const ACCEPTED_EXTENSIONS = [".pdf", ".docx"];

const STAGES = ["Reading your file", "Finding education, roles, and skills", "Checking every item against your resume"];
const STAGE_INTERVAL_MS = 1800;

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
  const [fileName, setFileName] = useState<string | null>(null);
  const [stage, setStage] = useState(0);
  const [result, setResult] = useState<ResumeExtractionResult | null>(null);
  const reduce = useReducedMotion();

  // Advance the stage labels while the request runs. They describe what the
  // server does; the last one holds until the response arrives.
  useEffect(() => {
    if (!isUploading) return;
    const timer = window.setInterval(
      () => setStage((current) => Math.min(current + 1, STAGES.length - 1)),
      STAGE_INTERVAL_MS
    );
    return () => window.clearInterval(timer);
  }, [isUploading]);

  function validate(file: File): string | null {
    const lower = file.name.toLowerCase();
    if (!ACCEPTED_EXTENSIONS.some((ext) => lower.endsWith(ext))) {
      return "Please upload a .pdf or .docx file.";
    }
    if (file.size > MAX_SIZE_BYTES) {
      return "That file is too large. Maximum size is 4MB.";
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
    setFileName(file.name);
    setStage(0);
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
            if (file && !isUploading) handleFile(file);
          }}
          className={cn(
            "relative flex min-h-[188px] flex-col items-center justify-center gap-3 overflow-hidden rounded-[var(--radius-md)] border border-dashed px-6 py-10 text-center transition-[border-color,background-color,transform] duration-200",
            isDragging
              ? "scale-[1.01] border-[var(--color-accent)] bg-[var(--color-accent-subtle)]"
              : "border-[var(--color-border-strong)]"
          )}
        >
          <AnimatePresence mode="wait" initial={false}>
            {isUploading ? (
              <motion.div
                key="uploading"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                className="flex w-full max-w-xs flex-col items-center"
                role="status"
                aria-live="polite"
              >
                <div className="relative flex size-11 items-center justify-center rounded-[12px] bg-[var(--color-accent-subtle)]">
                  <FileText className="size-5 text-[var(--color-accent)]" aria-hidden />
                  {/* Scan line sweeping the document icon. */}
                  {!reduce && (
                    <motion.span
                      aria-hidden
                      className="absolute inset-x-1.5 top-[9px] h-0.5 rounded-full bg-[var(--color-accent)]/70"
                      animate={{ y: [0, 24, 0] }}
                      transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
                    />
                  )}
                </div>
                <p className="mt-3 max-w-full truncate text-[12.5px] text-[var(--color-text-tertiary)]">{fileName}</p>
                <ul className="mt-4 w-full space-y-2 text-left">
                  {STAGES.map((label, i) => {
                    const done = i < stage;
                    const active = i === stage;
                    return (
                      <li
                        key={label}
                        className={cn(
                          "flex items-center gap-2.5 text-[13px] transition-colors duration-300",
                          done && "text-[var(--color-text-secondary)]",
                          active && "font-medium text-[var(--color-text-primary)]",
                          !done && !active && "text-[var(--color-text-tertiary)]/70"
                        )}
                      >
                        <span className="flex size-4 items-center justify-center">
                          {done ? (
                            <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }} className="flex">
                              <Check className="size-4 text-[var(--color-success)]" aria-hidden />
                            </motion.span>
                          ) : active ? (
                            <Loader2 className="size-3.5 animate-spin text-[var(--color-accent)]" aria-hidden />
                          ) : (
                            <span className="size-1.5 rounded-full bg-[var(--color-border-strong)]" aria-hidden />
                          )}
                        </span>
                        {label}
                      </li>
                    );
                  })}
                </ul>
              </motion.div>
            ) : (
              <motion.div
                key="idle"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                className="flex flex-col items-center gap-3"
              >
                <motion.span
                  animate={isDragging && !reduce ? { y: -4 } : { y: 0 }}
                  transition={{ type: "spring", stiffness: 300, damping: 18 }}
                  className="flex size-11 items-center justify-center rounded-[12px] bg-[var(--color-bg-subtle)]"
                >
                  <UploadCloud className="size-5 text-[var(--color-text-tertiary)]" aria-hidden />
                </motion.span>
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
                  <p className="mt-1 text-[12.5px] text-[var(--color-text-tertiary)]">
                    PDF or DOCX, up to 4MB. You review everything before it&apos;s added.
                  </p>
                  {currentFilename && (
                    <p className="mt-1 text-[12.5px] text-[var(--color-text-tertiary)]">
                      Last uploaded: {currentFilename}
                    </p>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
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
