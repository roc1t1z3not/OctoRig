"use client";
import "./creator.css";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Send, FileText } from "lucide-react";
import {
  getMySubmissions,
  createSubmission,
  submitForReview,
  type ContentStatus,
  type ContentType,
  type ContentSubmission,
} from "@/lib/api/content";
import { useNotificationsStore } from "@/stores/notifications.store";

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
    <span
      className="status-badge"
      style={{ background: s.bg, color: s.color }}
    >
      {status.replace("_", " ")}
    </span>
  );
}

function CreateModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const [title, setTitle] = useState("");
  const [contentType, setContentType] = useState<ContentType>("challenge");

  const { mutate, isPending } = useMutation({
    mutationFn: () =>
      createSubmission({ content_type: contentType, title, body: {} }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["content", "mine"] });
      push("success", "Draft created.");
      onClose();
    },
    onError: () => push("error", "Failed to create draft."),
  });

  return (
    <div className="modal-backdrop" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className="modal-box">
        <h2 className="modal-title">New Draft</h2>

        <div className="modal-field">
          <label className="modal-label">Title</label>
          <input
            className="g-input"
            placeholder="Submission title…"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            autoFocus
          />
        </div>

        <div className="modal-field">
          <label className="modal-label">Type</label>
          <select
            className="g-input"
            value={contentType}
            onChange={(e) => setContentType(e.target.value as ContentType)}
          >
            <option value="challenge">Challenge</option>
            <option value="lab">Lab</option>
          </select>
        </div>

        <div className="modal-footer">
          <button className="g-btn g-btn-ghost" onClick={onClose}>Cancel</button>
          <button
            className="g-btn g-btn-primary"
            disabled={!title.trim() || isPending}
            onClick={() => mutate()}
          >
            {isPending ? "Creating…" : "Create Draft"}
          </button>
        </div>
      </div>
    </div>
  );
}

function SubmissionRow({ sub }: { sub: ContentSubmission }) {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const [expanded, setExpanded] = useState(false);

  const { mutate: submit, isPending } = useMutation({
    mutationFn: () => submitForReview(sub.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["content", "mine"] });
      push("success", "Submitted for review.");
    },
    onError: () => push("error", "Failed to submit."),
  });

  return (
    <>
      <tr>
        <td style={{ color: "var(--g-text)" }}>{sub.title}</td>
        <td>
          <span className="status-badge" style={{ background: "color-mix(in srgb, var(--g-accent) 10%, transparent)", color: "var(--g-accent)" }}>
            {sub.content_type}
          </span>
        </td>
        <td><StatusBadge status={sub.status} /></td>
        <td style={{ color: "var(--g-text-muted)", fontFamily: "var(--font-mono, monospace)", fontSize: "0.75rem" }}>
          {new Date(sub.updated_at).toLocaleDateString()}
        </td>
        <td>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {sub.status === "draft" && (
              <button
                className="g-btn g-btn-ghost g-btn-sm"
                disabled={isPending}
                onClick={() => submit()}
                title="Submit for review"
              >
                <Send size={12} />
                Submit
              </button>
            )}
            <button
              className={`g-btn g-btn-sm ${expanded ? "g-btn-subtle" : "g-btn-ghost"}`}
              onClick={() => setExpanded((v) => !v)}
            >
              <FileText size={12} />
              {expanded ? "Hide" : "View"}
            </button>
          </div>
        </td>
      </tr>
      {expanded && (
        <tr>
          <td colSpan={5} style={{ padding: "0 0.75rem 0.75rem" }}>
            <div style={{
              background: "var(--g-surface)",
              border: "1px solid var(--g-border)",
              borderRadius: "4px",
              padding: "0.75rem",
            }}>
              <div style={{ fontSize: "0.625rem", textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--g-text-muted)", marginBottom: "0.5rem" }}>
                Body
              </div>
              {Object.keys(sub.body).length === 0 ? (
                <span style={{ fontSize: "0.75rem", color: "var(--g-text-muted)", fontStyle: "italic" }}>
                  Empty — no body content yet.
                </span>
              ) : (
                <pre style={{ margin: 0, fontSize: "0.75rem", color: "var(--g-text-secondary)", whiteSpace: "pre-wrap", wordBreak: "break-all", fontFamily: "var(--font-mono, monospace)" }}>
                  {JSON.stringify(sub.body, null, 2)}
                </pre>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

export default function CreatorPage() {
  const [showCreate, setShowCreate] = useState(false);

  const { data: submissions = [], isLoading } = useQuery({
    queryKey: ["content", "mine"],
    queryFn: () => getMySubmissions(),
  });

  return (
    <div className="page">
      <div className="creator-header page-header">
        <h1 className="page-title font-mono">Content Creator</h1>
        <button className="g-btn g-btn-primary" onClick={() => setShowCreate(true)}>
          <Plus size={14} />
          New Draft
        </button>
      </div>

      {isLoading ? (
        <div className="text-muted text-sm mt-4">Loading…</div>
      ) : submissions.length === 0 ? (
        <div className="creator-empty">
          No submissions yet. Create a draft to get started.
        </div>
      ) : (
        <div className="creator-table-wrap">
          <table className="g-table">
            <thead>
              <tr>
                <th>Title</th>
                <th>Type</th>
                <th>Status</th>
                <th>Last Updated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {submissions.map((sub) => (
                <SubmissionRow key={sub.id} sub={sub} />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showCreate && <CreateModal onClose={() => setShowCreate(false)} />}
    </div>
  );
}
