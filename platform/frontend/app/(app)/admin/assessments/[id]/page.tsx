"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../../admin.css";
import "../../settings/settings.css";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Copy, Check, Plus, ChevronDown, ChevronRight, Shield } from "lucide-react";
import Link from "next/link";
import {
  getAssessment,
  listInvites,
  createInvite,
  revokeInvite,
  getCandidateProgress,
  type AssessmentInvite,
  type AssessmentInviteWithProgress,
  type InviteStatus,
} from "@/lib/api/assessments";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";

function StatusBadge({ status }: { status: InviteStatus }) {
  const colors: Record<InviteStatus, string> = {
    pending: "var(--g-text-muted)",
    accepted: "var(--g-warning, #f59e0b)",
    active: "var(--g-accent)",
    expired: "var(--g-danger)",
    revoked: "var(--g-danger)",
  };
  return (
    <span
      style={{
        fontSize: "0.7rem",
        fontFamily: "var(--font-mono, monospace)",
        color: colors[status],
        textTransform: "uppercase",
        letterSpacing: "0.04em",
      }}
    >
      {status}
    </span>
  );
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      className="g-btn g-btn-ghost g-btn-sm"
      title="Copy invite link"
      onClick={() => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 1500);
      }}
    >
      {copied ? <Check size={12} /> : <Copy size={12} />}
    </button>
  );
}

function ProgressRow({
  assessmentId,
  invite,
}: {
  assessmentId: number;
  invite: AssessmentInvite;
}) {
  const [expanded, setExpanded] = useState(false);
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();
  const qc = useQueryClient();

  const { data: progress, isLoading } = useQuery<AssessmentInviteWithProgress>({
    queryKey: ["assessment-invite-progress", assessmentId, invite.id],
    queryFn: () => getCandidateProgress(assessmentId, invite.id),
    enabled: expanded,
  });

  const revokeMutation = useMutation({
    mutationFn: () => revokeInvite(assessmentId, invite.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["assessment-invites", assessmentId] });
      push("success", "Invite revoked");
    },
    onError: () => push("error", "Failed to revoke invite"),
  });

  const inviteUrl =
    typeof window !== "undefined"
      ? `${window.location.origin}/assessment/invite/${invite.token}`
      : `/assessment/invite/${invite.token}`;

  return (
    <>
      <tr
        style={{ cursor: "pointer" }}
        onClick={() => setExpanded((v) => !v)}
      >
        <td>
          {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        </td>
        <td style={{ color: "var(--g-text)" }}>{invite.email}</td>
        <td style={{ color: "var(--g-text-muted)", fontSize: "0.8rem" }}>
          {invite.candidate_name ?? "—"}
        </td>
        <td><StatusBadge status={invite.status} /></td>
        <td style={{ color: "var(--g-text-muted)", fontSize: "0.75rem", fontFamily: "var(--font-mono, monospace)" }}>
          {invite.started_at ? new Date(invite.started_at).toLocaleString() : "—"}
        </td>
        <td style={{ color: "var(--g-text-muted)", fontSize: "0.75rem", fontFamily: "var(--font-mono, monospace)" }}>
          {invite.expires_at ? new Date(invite.expires_at).toLocaleString() : "—"}
        </td>
        <td style={{ fontSize: "0.8rem", color: "var(--g-text-muted)" }}>
          {invite.deployment_ids.length > 0 ? `${invite.deployment_ids.length} labs` : "—"}
        </td>
        <td>
          <div style={{ display: "flex", gap: 6 }} onClick={(e) => e.stopPropagation()}>
            <CopyButton text={inviteUrl} />
            {!invite.is_revoked && (
              <button
                className="g-btn g-btn-ghost g-btn-sm"
                style={{ color: "var(--g-danger)" }}
                onClick={() =>
                  confirm({
                    title: "Revoke invite?",
                    body: `This will block ${invite.email} from starting or continuing the assessment.`,
                    confirmLabel: "Revoke",
                    dangerous: true,
                    onConfirm: () => revokeMutation.mutate(),
                  })
                }
              >
                Revoke
              </button>
            )}
          </div>
        </td>
      </tr>

      {expanded && (
        <tr>
          <td colSpan={8} style={{ background: "var(--g-surface-elevated, var(--g-surface))", padding: "12px 20px" }}>
            {isLoading ? (
              <span className="text-muted text-sm">Loading progress…</span>
            ) : progress ? (
              <div style={{ display: "flex", gap: 32 }}>
                <div>
                  <div style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--g-text-muted)", marginBottom: 6 }}>
                    Flags Solved ({progress.flags_solved.length})
                  </div>
                  {progress.flags_solved.length === 0 ? (
                    <span className="text-muted" style={{ fontSize: "0.8rem" }}>None yet</span>
                  ) : (
                    <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "flex", flexDirection: "column", gap: 4 }}>
                      {progress.flags_solved.map((f) => (
                        <li key={f.challenge_slug} style={{ fontSize: "0.8rem", display: "flex", alignItems: "center", gap: 6 }}>
                          <Shield size={11} style={{ color: "var(--g-accent)" }} />
                          <span style={{ color: "var(--g-text)" }}>{f.challenge_title}</span>
                          <span style={{ color: "var(--g-text-muted)", fontSize: "0.7rem" }}>
                            {new Date(f.solved_at).toLocaleString()}
                          </span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
                <div>
                  <div style={{ fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.06em", color: "var(--g-text-muted)", marginBottom: 6 }}>
                    Report
                  </div>
                  <span
                    className={`role-pill ${progress.report_submitted ? "role-pill--on" : "role-pill--off"}`}
                    style={{ fontSize: "0.75rem" }}
                  >
                    {progress.report_submitted ? "Submitted" : "Not submitted"}
                  </span>
                </div>
              </div>
            ) : null}
          </td>
        </tr>
      )}
    </>
  );
}

export default function AssessmentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const assessmentId = Number(id);
  const { push } = useNotificationsStore();
  const qc = useQueryClient();

  const [newEmail, setNewEmail] = useState("");
  const [newName, setNewName] = useState("");

  const { data: assessment, isLoading: assessmentLoading } = useQuery({
    queryKey: ["admin-assessment", assessmentId],
    queryFn: () => getAssessment(assessmentId),
  });

  const { data: invites = [], isLoading: invitesLoading } = useQuery({
    queryKey: ["assessment-invites", assessmentId],
    queryFn: () => listInvites(assessmentId),
  });

  const inviteMutation = useMutation({
    mutationFn: () =>
      createInvite(assessmentId, {
        email: newEmail,
        candidate_name: newName || undefined,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["assessment-invites", assessmentId] });
      qc.invalidateQueries({ queryKey: ["admin-assessments"] });
      push("success", `Invite created for ${newEmail}`);
      setNewEmail("");
      setNewName("");
    },
    onError: (err: any) =>
      push("error", err?.response?.data?.detail ?? "Failed to create invite"),
  });

  if (assessmentLoading) {
    return (
      <div className="page">
        <p className="text-muted text-sm">Loading…</p>
      </div>
    );
  }

  if (!assessment) {
    return (
      <div className="page">
        <p className="text-muted text-sm">Assessment not found.</p>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <Link href="/admin/assessments" className="g-btn g-btn-ghost g-btn-sm">
          <ArrowLeft size={14} /> Back
        </Link>
        <h1 className="page-title font-mono">{assessment.name}</h1>
        <span
          className={`role-pill ${assessment.is_active ? "role-pill--on" : "role-pill--off"}`}
        >
          {assessment.is_active ? "active" : "inactive"}
        </span>
      </div>

      {/* Assessment summary */}
      <div className="g-card" style={{ padding: "16px 20px", marginBottom: 24, display: "flex", gap: 32, flexWrap: "wrap" }}>
        <div>
          <div className="text-11 text-muted" style={{ marginBottom: 2 }}>Labs</div>
          <div style={{ fontFamily: "var(--font-mono, monospace)", fontSize: "0.875rem", color: "var(--g-text)" }}>
            {assessment.lab_slugs.map((slug) => {
              const display = assessment.lab_display_names[slug];
              return (
                <div key={slug}>
                  {display ? (
                    <><span style={{ color: "var(--g-text)" }}>{display}</span><span style={{ color: "var(--g-text-muted)", fontSize: "0.7rem" }}> ({slug})</span></>
                  ) : slug}
                </div>
              );
            })}
          </div>
        </div>
        <div>
          <div className="text-11 text-muted" style={{ marginBottom: 2 }}>Duration</div>
          <div style={{ fontSize: "0.875rem", color: "var(--g-text)" }}>{assessment.duration_hours}h</div>
        </div>
        {assessment.company_name && (
          <div>
            <div className="text-11 text-muted" style={{ marginBottom: 2 }}>Company</div>
            <div style={{ fontSize: "0.875rem", color: "var(--g-text)" }}>{assessment.company_name}</div>
          </div>
        )}
        <div>
          <div className="text-11 text-muted" style={{ marginBottom: 2 }}>Candidates</div>
          <div style={{ fontSize: "0.875rem", color: "var(--g-text)" }}>
            {assessment.active_invite_count} active / {assessment.invite_count} total
          </div>
        </div>
      </div>

      {/* Add candidate */}
      <section className="settings-section" style={{ marginBottom: 24 }}>
        <h2 className="settings-section-title">Add Candidate</h2>
        <div style={{ display: "flex", gap: 10, alignItems: "flex-end", flexWrap: "wrap", padding: "12px 16px" }}>
          <div className="ev-field" style={{ flexShrink: 0, minWidth: 220 }}>
            <label className="ev-label">Email *</label>
            <input
              className="g-input"
              type="email"
              placeholder="candidate@example.com"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
            />
          </div>
          <div className="ev-field" style={{ flexShrink: 0, minWidth: 180 }}>
            <label className="ev-label">Name (optional)</label>
            <input
              className="g-input"
              placeholder="Jane Smith"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
            />
          </div>
          <button
            className="g-btn g-btn-primary g-btn-sm"
            disabled={!newEmail || inviteMutation.isPending}
            onClick={() => inviteMutation.mutate()}
          >
            <Plus size={13} />
            {inviteMutation.isPending ? "Creating…" : "Generate Invite"}
          </button>
        </div>
      </section>

      {/* Candidates table */}
      <section>
        <h2 className="section-title text-11 text-muted" style={{ marginBottom: "0.75rem" }}>
          Candidates ({invites.length})
        </h2>

        {invitesLoading ? (
          <p className="text-muted text-sm">Loading…</p>
        ) : invites.length === 0 ? (
          <p className="text-muted text-sm">No invites yet. Add candidates above.</p>
        ) : (
          <table className="g-table">
            <thead>
              <tr>
                <th style={{ width: 24 }}></th>
                <th>Email</th>
                <th>Name</th>
                <th>Status</th>
                <th>Started</th>
                <th>Expires</th>
                <th>Labs</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {invites.map((invite) => (
                <ProgressRow key={invite.id} assessmentId={assessmentId} invite={invite} />
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
