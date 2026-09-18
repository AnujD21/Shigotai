import type { ApplicationStatus } from "@/lib/types";

export const STATUS_ORDER: ApplicationStatus[] = [
  "SAVED",
  "APPLIED",
  "INTERVIEW",
  "OFFER",
  "REJECTED",
  "ARCHIVED",
];

export const STATUS_LABELS: Record<ApplicationStatus, string> = {
  SAVED: "Saved",
  APPLIED: "Applied",
  INTERVIEW: "Interview",
  OFFER: "Offer",
  REJECTED: "Rejected",
  ARCHIVED: "Archived",
};

export const STATUS_BADGE_TONE: Record<
  ApplicationStatus,
  "neutral" | "accent" | "success" | "warning" | "danger" | "info"
> = {
  SAVED: "neutral",
  APPLIED: "info",
  INTERVIEW: "warning",
  OFFER: "success",
  REJECTED: "danger",
  ARCHIVED: "neutral",
};
