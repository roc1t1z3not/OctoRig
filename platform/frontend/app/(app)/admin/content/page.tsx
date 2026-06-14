"use client";
import "../admin.css";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { CheckCircle, XCircle, Clock, Printer } from "lucide-react";
import {
  getPendingQueue,
  getApprovedQueue,
  claimSubmission,
  reviewSubmission,
  publishSubmission,
  type ContentSubmission,
  type ReviewVerdict,
  type ContentStatus,
} from "@/lib/api/content";
import { useNotificationsStore } from "@/stores/notifications.store";

type Tab = "pending" | "approved";

const STATUS_STYLE: Record<ContentStatus, { bg: string; color: string }> = {
  draft:          { bg: "color-mix(in srgb, var(--g-text-muted) 15%, transparent)", color: "var(--g-text-muted)" },
  pending_review: { bg: "color-mix(in srgb, var(--g-warning) 15%, transparent)",    color: "var(--g-warning)" },
  in_review:      { bg: "color-mix(in srgb, var(--g-accent) 15%, transparent)",     color: "var(--g-accent)" },
  approved:       { bg: "color-mix(in srgb, var(--g-success) 15%, transparent)",    color: "var(--g-success)" },
  published:      { bg: "color-mix(in srgb, var(--g-success) 15%, transparent)",    color: "var(--g-success)" },
  rejected:       { bg: "color-mix(in srgb, var(--g-danger) 15%, transparent)",     color: "var(--g-danger)" },
};

function StatusBadge({ status }: { status: ContentStatus }) {
  const s = STATUS_STYLE[status];
  return (
    <span className="role-pill" style={{ background: s.bg, color: s.color }}>
      {status.replace("_", " ")}
    </span>
  );
}

function ReviewForm({
  subId,
  onDone,
}: {
  subId: number;
  onDone: () => void;
}) {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const [verdict, setVerdict] = useState<ReviewVerdict>("approved");
  const [comment, setComment] = useState("");

  const { mutate, isPending } = useMutation({
    mutationFn: () => reviewSubmission(subId, verdict, comment || undefined),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["content", "queue", "pending"] });
      push("success", `Verdict submitted: ${verdict}`);
      onDone();
    },
    onError: () => push("error", "Failed to submit review."),
  });

  return (
    <div
      style={{
        marginTop: "0.5rem",
        padding: "0.75rem",
        background: "var(--g-surface)",
        border: "1px solid var(--g-border)",
        borderRadius: "4px",
        display: "flex",
        flexDirection: "column",
        gap: "0.5rem",
      }}
    >
      <div style={{ display: "flex", gap: "0.5rem" }}>
        {(["approved", "rejected", "needs_changes"] as ReviewVerdict[]).map((v) => (
          <button
            key={v}
            className={`g-btn g-btn-sm ${verdict === v ? "g-btn-primary" : "g-btn-ghost"}`}
            onClick={() => setVerdict(v)}
          >
            {v === "approved" && <CheckCircle size={12} />}
            {v === "rejected" && <XCircle size={12} />}
            {v === "needs_changes" && <Clock size={12} />}
            {v.replace("_", " ")}
          </button>
        ))}
      </div>
      <textarea
        className="g-input"
        rows={2}
        placeholder="Optional comment…"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        style={{ resize: "vertical", fontSize: "0.8125rem" }}
      />
      <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}>
        <button className="g-btn g-btn-ghost g-btn-sm" onClick={onDone}>Cancel</button>
        <button className="g-btn g-btn-primary g-btn-sm" disabled={isPending} onClick={() => mutate()}>
          {isPending ? "Submitting…" : "Submit Review"}
        </button>
      </div>
    </div>
  );
}

function BodyPreview({ body }: { body: Record<string, unknown> }) {
  return (
    <div style={{
      background: "var(--g-surface)", border: "1px solid var(--g-border)",
      borderRadius: "4px", padding: "0.75rem",
    }}>
      <div style={{ fontSize: "0.625rem", textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--g-text-muted)", marginBottom: "0.5rem" }}>
        Body
      </div>
      {Object.keys(body).length === 0 ? (
        <span style={{ fontSize: "0.75rem", color: "var(--g-text-muted)", fontStyle: "italic" }}>No body content.</span>
      ) : (
        <pre style={{ margin: 0, fontSize: "0.75rem", color: "var(--g-text-secondary)", whiteSpace: "pre-wrap", wordBreak: "break-all", fontFamily: "var(--font-mono, monospace)" }}>
          {JSON.stringify(body, null, 2)}
        </pre>
      )}
    </div>
  );
}

function PendingRow({ sub }: { sub: ContentSubmission }) {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const [showReview, setShowReview] = useState(false);
  const [showBody, setShowBody] = useState(false);

  const { mutate: claim, isPending: claiming } = useMutation({
    mutationFn: () => claimSubmission(sub.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["content", "queue", "pending"] });
      push("success", "Submission claimed.");
    },
    onError: () => push("error", "Failed to claim submission."),
  });

  const isClaimed = sub.status === "in_review";

  return (
    <>
      <tr>
        <td>
          <button
            className="g-btn g-btn-ghost g-btn-sm"
            style={{ padding: "0.1rem 0.4rem", fontSize: "0.7rem" }}
            onClick={() => setShowBody((v) => !v)}
            title="Toggle body"
          >
            {showBody ? "▾" : "▸"}
          </button>
          {" "}
          <span style={{ color: "var(--g-text)" }}>{sub.title}</span>
        </td>
        <td>
          <span className="role-pill role-pill--on">{sub.content_type}</span>
        </td>
        <td style={{ color: "var(--g-text-muted)", fontFamily: "var(--font-mono, monospace)", fontSize: "0.75rem" }}>
          #{sub.author_id}
        </td>
        <td><StatusBadge status={sub.status} /></td>
        <td>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {!isClaimed && (
              <button
                className="g-btn g-btn-ghost g-btn-sm"
                disabled={claiming}
                onClick={() => claim()}
              >
                {claiming ? "Claiming…" : "Claim"}
              </button>
            )}
            {isClaimed && (
              <button
                className="g-btn g-btn-primary g-btn-sm"
                onClick={() => setShowReview((v) => !v)}
              >
                Review
              </button>
            )}
          </div>
        </td>
      </tr>
      {showBody && (
        <tr>
          <td colSpan={5} style={{ padding: "0 0.75rem 0.5rem" }}>
            <BodyPreview body={sub.body} />
          </td>
        </tr>
      )}
      {showReview && isClaimed && (
        <tr>
          <td colSpan={5} style={{ padding: "0 0.75rem 0.75rem" }}>
            <ReviewForm subId={sub.id} onDone={() => setShowReview(false)} />
          </td>
        </tr>
      )}
    </>
  );
}

function ApprovedRow({ sub }: { sub: ContentSubmission }) {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const [showBody, setShowBody] = useState(false);

  const { mutate: publish, isPending } = useMutation({
    mutationFn: () => publishSubmission(sub.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["content", "queue", "approved"] });
      push("success", "Submission published.");
    },
    onError: () => push("error", "Failed to publish."),
  });

  return (
    <>
      <tr>
        <td>
          <button
            className="g-btn g-btn-ghost g-btn-sm"
            style={{ padding: "0.1rem 0.4rem", fontSize: "0.7rem" }}
            onClick={() => setShowBody((v) => !v)}
            title="Toggle body"
          >
            {showBody ? "▾" : "▸"}
          </button>
          {" "}
          <span style={{ color: "var(--g-text)" }}>{sub.title}</span>
        </td>
        <td>
          <span className="role-pill role-pill--on">{sub.content_type}</span>
        </td>
        <td style={{ color: "var(--g-text-muted)", fontFamily: "var(--font-mono, monospace)", fontSize: "0.75rem" }}>
          #{sub.author_id}
        </td>
        <td><StatusBadge status={sub.status} /></td>
        <td>
          <button
            className="g-btn g-btn-primary g-btn-sm"
            disabled={isPending}
            onClick={() => publish()}
          >
            <Printer size={12} />
            {isPending ? "Publishing…" : "Publish"}
          </button>
        </td>
      </tr>
      {showBody && (
        <tr>
          <td colSpan={5} style={{ padding: "0 0.75rem 0.75rem" }}>
            <BodyPreview body={sub.body} />
          </td>
        </tr>
      )}
    </>
  );
}

export default function AdminContentPage() {
  const [tab, setTab] = useState<Tab>("pending");

  const { data: pending = [], isLoading: loadingPending } = useQuery({
    queryKey: ["content", "queue", "pending"],
    queryFn: getPendingQueue,
    enabled: tab === "pending",
  });

  const { data: approved = [], isLoading: loadingApproved } = useQuery({
    queryKey: ["content", "queue", "approved"],
    queryFn: getApprovedQueue,
    enabled: tab === "approved",
  });

  const isLoading = tab === "pending" ? loadingPending : loadingApproved;
  const rows = tab === "pending" ? pending : approved;

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Content Review</h1>
      </div>

      <div className="flex gap-1 mb-4">
        <button
          className={`g-btn ${tab === "pending" ? "g-btn-primary" : "g-btn-ghost"}`}
          onClick={() => setTab("pending")}
        >
          Pending
        </button>
        <button
          className={`g-btn ${tab === "approved" ? "g-btn-primary" : "g-btn-ghost"}`}
          onClick={() => setTab("approved")}
        >
          Approved
        </button>
      </div>

      {isLoading ? (
        <div className="text-muted text-sm">Loading…</div>
      ) : rows.length === 0 ? (
        <div className="text-muted text-sm mt-4">No submissions in this queue.</div>
      ) : (
        <table className="g-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Type</th>
              <th>Author ID</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {tab === "pending"
              ? pending.map((sub) => <PendingRow key={sub.id} sub={sub} />)
              : approved.map((sub) => <ApprovedRow key={sub.id} sub={sub} />)
            }
          </tbody>
        </table>
      )}
    </div>
  );
}
