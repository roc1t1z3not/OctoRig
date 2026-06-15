"use client";
import type { ContentStatus } from "@/lib/api/content";

const STATUS_STYLE: Record<ContentStatus, { bg: string; color: string }> = {
  draft:          { bg: "color-mix(in srgb, var(--g-text-muted) 15%, transparent)", color: "var(--g-text-muted)" },
  pending_review: { bg: "color-mix(in srgb, var(--g-warning) 15%, transparent)",    color: "var(--g-warning)" },
  in_review:      { bg: "color-mix(in srgb, var(--g-accent) 15%, transparent)",     color: "var(--g-accent)" },
  approved:       { bg: "color-mix(in srgb, var(--g-success) 15%, transparent)",    color: "var(--g-success)" },
  published:      { bg: "color-mix(in srgb, var(--g-success) 15%, transparent)",    color: "var(--g-success)" },
  rejected:       { bg: "color-mix(in srgb, var(--g-danger) 15%, transparent)",     color: "var(--g-danger)" },
};

export function StatusBadge({ status }: { status: ContentStatus }) {
  const s = STATUS_STYLE[status];
  return (
    <span className="status-badge" style={{ background: s.bg, color: s.color }}>
      {status.replace("_", " ")}
    </span>
  );
}
