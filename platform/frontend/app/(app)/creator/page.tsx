"use client";
import "./creator.css";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Send, FileText, Edit3, X } from "lucide-react";
import {
  getMySubmissions,
  createSubmission,
  submitForReview,
  updateSubmission,
  type ContentStatus,
  type ContentType,
  type ContentSubmission,
  type FlagInput,
  type HintInput,
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

function ChallengeBodyEditor({ sub }: { sub: ContentSubmission }) {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const body = sub.body as any;

  const [description, setDescription] = useState<string>(body.description ?? "");
  const [difficulty, setDifficulty] = useState<string>(body.difficulty ?? "easy");
  const [category, setCategory] = useState<string>(body.category ?? "");
  const [challengeType, setChallengeType] = useState<string>(body.challenge_type ?? "flag");
  const [points, setPoints] = useState<number>(body.points ?? 100);
  const [estMinutes, setEstMinutes] = useState<string>(body.estimated_minutes?.toString() ?? "");
  const [tags, setTags] = useState<string>(Array.isArray(body.tags) ? body.tags.join(", ") : "");
  const [codeSnippet, setCodeSnippet] = useState<string>(body.code_snippet ?? "");
  const [language, setLanguage] = useState<string>(body.language ?? "python");
  const [flags, setFlags] = useState<FlagInput[]>(
    body.flags?.length ? body.flags : [{ value: "", flag_type: "static", case_sensitive: true }]
  );
  const [hints, setHints] = useState<HintInput[]>(body.hints ?? []);

  function buildBody() {
    const base: Record<string, unknown> = {
      description,
      difficulty,
      category,
      challenge_type: challengeType,
      points,
      estimated_minutes: estMinutes ? parseInt(estMinutes, 10) : undefined,
      tags: tags.split(",").map((t) => t.trim()).filter(Boolean),
      flags,
      hints: hints.map((h, i) => ({ ...h, order_num: i + 1 })),
    };
    if (challengeType === "short_answer") {
      base.code_snippet = codeSnippet;
      base.language = language;
    }
    return base;
  }

  const canSubmit = flags.some((f) => f.value.trim() !== "");

  const saveMutation = useMutation({
    mutationFn: () => updateSubmission(sub.id, { body: buildBody() }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["content", "mine"] });
      push("success", "Draft saved.");
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Save failed."),
  });

  const submitMutation = useMutation({
    mutationFn: async () => {
      await updateSubmission(sub.id, { body: buildBody() });
      return submitForReview(sub.id);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["content", "mine"] });
      push("success", "Submitted for review.");
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Submission failed."),
  });

  const fieldStyle = { display: "flex", flexDirection: "column" as const, gap: "0.25rem" };
  const labelStyle = { fontSize: "0.6875rem", textTransform: "uppercase" as const, letterSpacing: "0.07em", color: "var(--g-text-muted)" };
  const sectionStyle = { borderTop: "1px solid var(--g-border)", paddingTop: "0.75rem", marginTop: "0.25rem" };

  return (
    <div style={{
      background: "var(--g-surface)",
      border: "1px solid var(--g-border)",
      borderRadius: "4px",
      padding: "1rem",
      display: "flex",
      flexDirection: "column",
      gap: "0.75rem",
    }}>

      {/* Core */}
      <div style={fieldStyle}>
        <label style={labelStyle}>Description *</label>
        <textarea
          className="g-input"
          rows={4}
          placeholder="Describe the challenge scenario without revealing the technique…"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          style={{ resize: "vertical" }}
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0.5rem" }}>
        <div style={fieldStyle}>
          <label style={labelStyle}>Difficulty *</label>
          <select className="g-input" value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>
            <option value="insane">Insane</option>
          </select>
        </div>
        <div style={fieldStyle}>
          <label style={labelStyle}>Category *</label>
          <input
            className="g-input"
            list="category-suggestions"
            placeholder="e.g. sqli, xss, web…"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          />
          <datalist id="category-suggestions">
            {["sqli", "xss", "idor", "web", "recon", "crypto", "forensics", "pwn", "rev"].map((c) => (
              <option key={c} value={c} />
            ))}
          </datalist>
        </div>
        <div style={fieldStyle}>
          <label style={labelStyle}>Challenge Type</label>
          <select className="g-input" value={challengeType} onChange={(e) => setChallengeType(e.target.value)}>
            <option value="flag">Flag</option>
            <option value="short_answer">Coding Challenge</option>
            <option value="web">Web</option>
            <option value="container">Container</option>
            <option value="mcq">MCQ</option>
          </select>
        </div>
      </div>

      {/* Code snippet — only for coding challenges */}
      {challengeType === "short_answer" && (
        <div style={sectionStyle}>
          <div style={{ display: "flex", gap: "0.5rem", alignItems: "flex-end", marginBottom: "0.5rem" }}>
            <div style={{ ...fieldStyle, flex: 1 }}>
              <label style={labelStyle}>Code Snippet</label>
            </div>
            <div style={fieldStyle}>
              <label style={labelStyle}>Language</label>
              <select className="g-input" style={{ width: "auto" }} value={language} onChange={(e) => setLanguage(e.target.value)}>
                {["python", "javascript", "typescript", "bash", "go", "rust", "java", "c", "cpp", "text"].map((l) => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
            </div>
          </div>
          <textarea
            className="g-input"
            rows={8}
            placeholder={"def mystery(x):\n    return x[::-1]\n\nprint(mystery(\"OctoRig\"))"}
            value={codeSnippet}
            onChange={(e) => setCodeSnippet(e.target.value)}
            style={{ resize: "vertical", fontFamily: "var(--font-mono, monospace)", fontSize: "0.8125rem" }}
          />
          <div style={{ fontSize: "0.6875rem", color: "var(--g-text-muted)", marginTop: "0.25rem" }}>
            The expected output (the answer) goes in the Flags section below.
          </div>
        </div>
      )}

      {/* Points & extras */}
      <div style={{ ...sectionStyle, display: "grid", gridTemplateColumns: "1fr 1fr 2fr", gap: "0.5rem" }}>
        <div style={fieldStyle}>
          <label style={labelStyle}>Points</label>
          <input
            className="g-input"
            type="number"
            min={1}
            value={points}
            onChange={(e) => setPoints(parseInt(e.target.value, 10) || 100)}
          />
        </div>
        <div style={fieldStyle}>
          <label style={labelStyle}>Est. Minutes</label>
          <input
            className="g-input"
            type="number"
            min={1}
            placeholder="optional"
            value={estMinutes}
            onChange={(e) => setEstMinutes(e.target.value)}
          />
        </div>
        <div style={fieldStyle}>
          <label style={labelStyle}>Tags (comma-separated)</label>
          <input
            className="g-input"
            placeholder="sqli, union, error-based…"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
          />
        </div>
      </div>

      {/* Flags */}
      <div style={sectionStyle}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
          <span style={labelStyle}>Flags * (at least one required)</span>
          <button
            className="g-btn g-btn-ghost g-btn-sm"
            onClick={() => setFlags((f) => [...f, { value: "", flag_type: "static", case_sensitive: true }])}
          >
            <Plus size={11} /> Add Flag
          </button>
        </div>
        {flags.map((flag, i) => (
          <div key={i} style={{ display: "grid", gridTemplateColumns: "1fr auto auto auto", gap: "0.4rem", alignItems: "center", marginBottom: "0.35rem" }}>
            <input
              className="g-input"
              placeholder={challengeType === "short_answer" ? "Expected output…" : "FLAG{...}"}
              value={flag.value}
              onChange={(e) => setFlags((f) => f.map((x, j) => j === i ? { ...x, value: e.target.value } : x))}
            />
            <select
              className="g-input"
              style={{ width: "auto" }}
              value={flag.flag_type}
              onChange={(e) => setFlags((f) => f.map((x, j) => j === i ? { ...x, flag_type: e.target.value as FlagInput["flag_type"] } : x))}
            >
              <option value="static">Static</option>
              <option value="dynamic">Dynamic</option>
              <option value="per_user">Per User</option>
              <option value="per_team">Per Team</option>
            </select>
            <label style={{ display: "flex", alignItems: "center", gap: "0.25rem", fontSize: "0.75rem", color: "var(--g-text-muted)", whiteSpace: "nowrap" }}>
              <input
                type="checkbox"
                checked={flag.case_sensitive}
                onChange={(e) => setFlags((f) => f.map((x, j) => j === i ? { ...x, case_sensitive: e.target.checked } : x))}
              />
              Case sensitive
            </label>
            <button
              className="g-btn g-btn-ghost g-btn-sm"
              style={{ color: "var(--g-danger)" }}
              disabled={flags.length === 1}
              onClick={() => setFlags((f) => f.filter((_, j) => j !== i))}
            >
              <X size={12} />
            </button>
          </div>
        ))}
      </div>

      {/* Hints */}
      <div style={sectionStyle}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
          <span style={labelStyle}>Hints (optional)</span>
          <button
            className="g-btn g-btn-ghost g-btn-sm"
            onClick={() => setHints((h) => [...h, { order_num: h.length + 1, content: "", cost: 0 }])}
          >
            <Plus size={11} /> Add Hint
          </button>
        </div>
        {hints.map((hint, i) => (
          <div key={i} style={{ display: "grid", gridTemplateColumns: "1fr auto auto", gap: "0.4rem", alignItems: "center", marginBottom: "0.35rem" }}>
            <input
              className="g-input"
              placeholder={`Hint ${i + 1}…`}
              value={hint.content}
              onChange={(e) => setHints((h) => h.map((x, j) => j === i ? { ...x, content: e.target.value } : x))}
            />
            <input
              className="g-input"
              type="number"
              min={0}
              style={{ width: "5rem" }}
              title="Cost (points)"
              placeholder="Cost"
              value={hint.cost}
              onChange={(e) => setHints((h) => h.map((x, j) => j === i ? { ...x, cost: parseInt(e.target.value, 10) || 0 } : x))}
            />
            <button
              className="g-btn g-btn-ghost g-btn-sm"
              style={{ color: "var(--g-danger)" }}
              onClick={() => setHints((h) => h.filter((_, j) => j !== i))}
            >
              <X size={12} />
            </button>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div style={{ display: "flex", gap: "0.5rem", justifyContent: "flex-end", borderTop: "1px solid var(--g-border)", paddingTop: "0.75rem" }}>
        <button
          className="g-btn g-btn-ghost g-btn-sm"
          disabled={saveMutation.isPending}
          onClick={() => saveMutation.mutate()}
        >
          {saveMutation.isPending ? "Saving…" : "Save Draft"}
        </button>
        <button
          className="g-btn g-btn-primary g-btn-sm"
          disabled={!canSubmit || submitMutation.isPending}
          onClick={() => submitMutation.mutate()}
        >
          <Send size={12} />
          {submitMutation.isPending ? "Submitting…" : "Save & Submit for Review"}
        </button>
      </div>
    </div>
  );
}

function SubmissionRow({ sub }: { sub: ContentSubmission }) {
  const [expanded, setExpanded] = useState(false);

  const isEditable = sub.status === "draft" || sub.status === "rejected";
  const showEditor = isEditable && sub.content_type === "challenge";

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
            <button
              className={`g-btn g-btn-sm ${expanded ? "g-btn-subtle" : "g-btn-ghost"}`}
              onClick={() => setExpanded((v) => !v)}
            >
              {isEditable ? <Edit3 size={12} /> : <FileText size={12} />}
              {expanded ? "Hide" : isEditable ? "Edit" : "View"}
            </button>
          </div>
        </td>
      </tr>
      {expanded && (
        <tr>
          <td colSpan={5} style={{ padding: "0 0.75rem 0.75rem" }}>
            {showEditor ? (
              <ChallengeBodyEditor sub={sub} />
            ) : (
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
            )}
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
