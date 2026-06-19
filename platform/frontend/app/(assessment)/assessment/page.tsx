"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { clsx } from "clsx";
import { Shield, Server, Clock, AlertTriangle, Play, Send, LayoutDashboard, FileText } from "lucide-react";
import {
  getAssessmentStatus,
  startAssessment,
  submitReport,
  type CandidateAssessmentStatus,
  type CandidateLabInfo,
} from "@/lib/api/assessments";
import { useUserStore } from "@/stores/user.store";
import { useNotificationsStore } from "@/stores/notifications.store";
import { MarkdownEditor } from "@/components/ui/MarkdownEditor";

// ---------------------------------------------------------------------------
// Countdown timer
// ---------------------------------------------------------------------------

function useCountdown(expiresAt: string | null) {
  const [remaining, setRemaining] = useState<number | null>(null);

  useEffect(() => {
    if (!expiresAt) { setRemaining(null); return; }
    const update = () => {
      const diff = Math.max(0, Math.floor((new Date(expiresAt).getTime() - Date.now()) / 1000));
      setRemaining(diff);
    };
    update();
    const id = setInterval(update, 1000);
    return () => clearInterval(id);
  }, [expiresAt]);

  return remaining;
}

function CountdownDisplay({ expiresAt }: { expiresAt: string | null }) {
  const remaining = useCountdown(expiresAt);

  if (remaining === null) return null;

  const expired = remaining === 0;
  const h = Math.floor(remaining / 3600);
  const m = Math.floor((remaining % 3600) / 60);
  const s = remaining % 60;
  const formatted = `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        fontFamily: "var(--font-mono, monospace)",
        fontSize: "1.2rem",
        fontWeight: 700,
        color: expired ? "var(--g-danger)" : remaining < 3600 ? "var(--g-warning, #f59e0b)" : "var(--g-text)",
      }}
    >
      <Clock size={18} />
      {expired ? "EXPIRED" : formatted}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Lab card
// ---------------------------------------------------------------------------

const STATUS_COLORS: Record<string, string> = {
  running: "var(--g-success, #22c55e)",
  starting: "var(--g-warning, #f59e0b)",
  stopping: "var(--g-warning, #f59e0b)",
  stopped: "var(--g-danger)",
  error: "var(--g-danger)",
};

function LabCard({ lab, expired }: { lab: CandidateLabInfo; expired: boolean }) {
  return (
    <div
      style={{
        background: "var(--g-card)",
        border: "1px solid var(--g-border)",
        borderRadius: 10,
        padding: "16px 20px",
        flex: "1 1 280px",
        minWidth: 260,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Server size={16} style={{ color: "var(--g-accent)" }} />
          <span style={{ fontWeight: 600, fontSize: "0.95rem", color: "var(--g-text)" }}>
            {lab.display_name}
          </span>
        </div>
        {lab.status && (
          <span
            style={{
              fontSize: "0.7rem",
              fontFamily: "var(--font-mono, monospace)",
              textTransform: "uppercase",
              color: STATUS_COLORS[lab.status] ?? "var(--g-text-muted)",
              letterSpacing: "0.04em",
            }}
          >
            {lab.status}
          </span>
        )}
      </div>

      {lab.status === "running" && lab.access_info.length > 0 && (
        <div
          style={{
            background: "var(--g-surface)",
            borderRadius: 6,
            padding: "10px 12px",
            marginBottom: 0,
            display: "flex",
            flexDirection: "column",
            gap: 4,
          }}
        >
          {lab.access_info.map((info) => (
            <div key={info.key} style={{ display: "flex", gap: 8, fontSize: "0.78rem" }}>
              <span style={{ color: "var(--g-text-muted)", minWidth: 40 }}>{info.key}</span>
              <code
                style={{
                  color: "var(--g-text)",
                  fontFamily: "var(--font-mono, monospace)",
                  fontSize: "0.75rem",
                  wordBreak: "break-all",
                }}
              >
                {info.value}
              </code>
            </div>
          ))}
        </div>
      )}

      {lab.status === "starting" && (
        <p style={{ color: "var(--g-text-muted)", fontSize: "0.8rem", margin: 0 }}>
          Container is starting up — this may take a minute…
        </p>
      )}

      {!lab.status && !expired && (
        <p style={{ color: "var(--g-text-muted)", fontSize: "0.8rem", margin: 0 }}>
          Not started yet.
        </p>
      )}

      {expired && (
        <p style={{ color: "var(--g-danger)", fontSize: "0.8rem", margin: 0 }}>
          Assessment expired — lab has been shut down.
        </p>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Report editor
// ---------------------------------------------------------------------------

const AUTOSAVE_DELAY_MS = 1500;

function timeAgo(date: Date, now: number): string {
  const s = Math.max(0, Math.floor((now - date.getTime()) / 1000));
  if (s < 5) return "just now";
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  return `${h}h ago`;
}

function ReportSection({
  content,
  onChange,
  alreadySubmitted,
  expired,
}: {
  content: string;
  onChange: (value: string) => void;
  alreadySubmitted: boolean;
  expired: boolean;
}) {
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [autosaving, setAutosaving] = useState(false);
  const [now, setNow] = useState(() => Date.now());
  const { push } = useNotificationsStore();
  const savedContentRef = useRef(content);

  // Tick once a second so "Saved Xs/Xm ago" stays live without re-saving.
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);

  const saveMutation = useMutation({
    mutationFn: (value: string) => submitReport(value),
    onSuccess: (_data, value) => {
      savedContentRef.current = value;
      setLastSaved(new Date());
    },
  });

  // Autosave a few seconds after the user stops typing — nothing is lost
  useEffect(() => {
    if (expired || content === savedContentRef.current) return;
    setAutosaving(true);
    const id = setTimeout(() => {
      saveMutation.mutate(content, { onSettled: () => setAutosaving(false) });
    }, AUTOSAVE_DELAY_MS);
    return () => clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [content, expired]);

  function saveNow() {
    saveMutation.mutate(content, {
      onSuccess: () => push("success", "Report saved"),
      onError: () => push("error", "Failed to save report"),
    });
  }

  return (
    <div
      style={{
        background: "var(--g-card)",
        border: "1px solid var(--g-border)",
        borderRadius: 10,
        padding: "20px 24px",
        marginTop: 32,
        display: "flex",
        flexDirection: "column",
        flex: 1,
        minHeight: 0,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Shield size={16} style={{ color: "var(--g-accent)" }} />
          <span style={{ fontWeight: 600, color: "var(--g-text)" }}>Pentest Report</span>
          {alreadySubmitted && (
            <span className="role-pill role-pill--on" style={{ fontSize: "0.7rem" }}>Submitted</span>
          )}
        </div>
        <span
          style={{
            display: "flex", alignItems: "center", gap: 6,
            fontSize: "0.75rem",
            color: autosaving ? "var(--g-accent)" : "var(--g-text-muted)",
          }}
        >
          {autosaving && (
            <span
              aria-hidden
              style={{
                width: 6, height: 6, borderRadius: "50%",
                background: "var(--g-accent)",
                animation: "pulse 1s ease-in-out infinite",
              }}
            />
          )}
          {autosaving
            ? "Saving…"
            : lastSaved
              ? `Saved ${timeAgo(lastSaved, now)} (${lastSaved.toLocaleTimeString()})`
              : "Not saved yet"}
        </span>
      </div>

      <MarkdownEditor
        value={content}
        onChange={onChange}
        disabled={expired}
        minHeight={520}
        fill
        placeholder={`# Pentest Report\n\n## Executive Summary\n...\n\n## Findings\n### Finding 1\n- **Severity**: High\n- **Location**: ...\n- **Description**: ...\n- **Proof of Concept**: ...\n- **Remediation**: ...\n\n## Flags Captured\n- FLAG{...} — ...`}
      />

      {!expired && (
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 10 }}>
          <button
            className="g-btn g-btn-primary g-btn-sm"
            disabled={saveMutation.isPending || !content.trim() || content === savedContentRef.current}
            onClick={saveNow}
          >
            <Send size={13} />
            {saveMutation.isPending ? "Saving…" : "Save Report"}
          </button>
          <span style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>
            Autosaves a couple seconds after you stop typing.
          </span>
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Sidebar nav
// ---------------------------------------------------------------------------

const SECTIONS = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "labs", label: "Labs", icon: Server },
  { id: "report", label: "Report", icon: FileText },
] as const;

type SectionId = (typeof SECTIONS)[number]["id"];

function WorkspaceSidebar({ active, onSelect }: { active: SectionId; onSelect: (id: SectionId) => void }) {
  return (
    <aside
      className="w-44 shrink-0 flex flex-col"
      style={{ borderRight: "1px solid var(--g-border)", background: "var(--g-chrome)" }}
    >
      <nav className="p-2 space-y-0.5">
        {SECTIONS.map(({ id, label, icon: Icon }) => {
          const isActive = active === id;
          return (
            <button
              key={id}
              onClick={() => onSelect(id)}
              className={clsx("g-nav-item w-full text-left", isActive && "active")}
              style={isActive ? {
                background: "var(--g-accent-dim)",
                color: "var(--g-text)",
                borderColor: "var(--g-border-hover)",
              } : undefined}
            >
              <Icon
                size={14}
                className="shrink-0"
                style={{ color: isActive ? "var(--g-accent)" : "var(--g-text-muted)" }}
              />
              <span style={{ color: isActive ? "var(--g-text)" : "var(--g-text-muted)" }}>
                {label}
              </span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}

// ---------------------------------------------------------------------------
// Main workspace
// ---------------------------------------------------------------------------

export default function AssessmentWorkspacePage() {
  const { accessToken, user, _hasHydrated, isRestoringToken } = useUserStore();
  const { push } = useNotificationsStore();
  const router = useRouter();
  const qc = useQueryClient();
  const [section, setSection] = useState<SectionId>("overview");
  const [reportContent, setReportContent] = useState<string | null>(null);

  useEffect(() => {
    if (_hasHydrated && !isRestoringToken && !accessToken) {
      router.replace("/login");
    }
  }, [_hasHydrated, isRestoringToken, accessToken, router]);

  const { data: status, isLoading } = useQuery<CandidateAssessmentStatus>({
    queryKey: ["assessment-status"],
    queryFn: getAssessmentStatus,
    enabled: !!accessToken && !!user?.is_candidate,
    refetchInterval: 30_000,
    retry: false,
  });

  useEffect(() => {
    if (status && reportContent === null) {
      setReportContent(status.report_content ?? "");
    }
  }, [status, reportContent]);

  const startMutation = useMutation({
    mutationFn: startAssessment,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["assessment-status"] });
      push("success", "Assessment started! Labs are booting…");
    },
    onError: (err: any) =>
      push("error", err?.response?.data?.detail ?? "Failed to start assessment"),
  });

  if (!_hasHydrated || isRestoringToken || !accessToken) return null;

  if (isLoading) {
    return (
      <div style={outerStyle}>
        <p style={{ color: "var(--g-text-muted)" }}>Loading your assessment…</p>
      </div>
    );
  }

  if (!status) {
    return (
      <div style={outerStyle}>
        <div style={{ textAlign: "center" }}>
          <AlertTriangle size={40} style={{ color: "var(--g-warning)", marginBottom: 12 }} />
          <h2 style={{ color: "var(--g-text)", marginBottom: 8 }}>No Active Assessment</h2>
          <p style={{ color: "var(--g-text-muted)" }}>
            Your invite could not be found. Please check that you used the correct link.
          </p>
        </div>
      </div>
    );
  }

  const expired = (status.time_remaining_seconds ?? 1) === 0;
  const notStarted = status.started_at === null;
  const companyName = status.company_name || "OctoRig";

  return (
    <div style={{ minHeight: "100vh", background: "var(--g-chrome)", padding: "0 0 60px" }}>
      {/* Header bar */}
      <div
        style={{
          background: "var(--g-card)",
          borderBottom: "1px solid var(--g-border)",
          padding: "12px 32px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          position: "sticky",
          top: 0,
          zIndex: 10,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          {status.company_logo_url ? (
            <img src={status.company_logo_url} alt={companyName} style={{ height: 28, objectFit: "contain" }} />
          ) : (
            <Shield size={22} style={{ color: "var(--g-accent)" }} />
          )}
          <span style={{ fontWeight: 600, color: "var(--g-text)", fontSize: "0.95rem" }}>
            {companyName}
          </span>
          <span style={{ color: "var(--g-border)" }}>·</span>
          <span style={{ color: "var(--g-text-muted)", fontSize: "0.85rem" }}>
            {status.assessment_name}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          {expired && (
            <span style={{ fontSize: "0.75rem", color: "var(--g-danger)", fontFamily: "var(--font-mono, monospace)" }}>
              ASSESSMENT ENDED
            </span>
          )}
          {!notStarted && <CountdownDisplay expiresAt={status.expires_at} />}
          <span style={{ fontSize: "0.8rem", color: "var(--g-text-muted)" }}>
            {user?.username}
          </span>
        </div>
      </div>

      {/* Body */}
      <div style={{ display: "flex", minHeight: "calc(100vh - 57px)" }}>
        <WorkspaceSidebar active={section} onSelect={setSection} />

        <div
          style={{
            flex: 1,
            maxWidth: section === "report" ? 1280 : 900,
            margin: "0 auto",
            padding: "32px 24px",
            display: "flex",
            flexDirection: "column",
            width: "100%",
          }}
        >
          {section === "overview" && (
            <>
              {status.candidate_instructions && (
                <div
                  style={{
                    background: "var(--g-card)",
                    border: "1px solid var(--g-border)",
                    borderRadius: 10,
                    padding: "16px 20px",
                    marginBottom: 28,
                    fontSize: "0.85rem",
                    color: "var(--g-text)",
                    lineHeight: 1.7,
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {status.candidate_instructions}
                </div>
              )}

              {notStarted && !expired && (
                <div
                  style={{
                    textAlign: "center",
                    padding: "40px 24px",
                    background: "var(--g-card)",
                    border: "1px solid var(--g-border)",
                    borderRadius: 12,
                    marginBottom: 28,
                  }}
                >
                  <Clock size={36} style={{ color: "var(--g-accent)", marginBottom: 12 }} />
                  <h2 style={{ color: "var(--g-text)", marginBottom: 8 }}>Ready to Begin?</h2>
                  <p style={{ color: "var(--g-text-muted)", marginBottom: 20, maxWidth: 400, margin: "0 auto 20px" }}>
                    Once you start, {status.labs.length} lab{status.labs.length !== 1 ? "s" : ""} will be
                    deployed for you and the <strong>{status.assessment_name}</strong> timer will begin.
                    You have <strong>{Math.floor(
                      (/* duration */ status.time_remaining_seconds ?? 0) / 3600 || 48
                    )}h</strong> to complete the assessment.
                  </p>
                  <button
                    className="g-btn g-btn-primary"
                    disabled={startMutation.isPending}
                    onClick={() => startMutation.mutate()}
                  >
                    <Play size={15} />
                    {startMutation.isPending ? "Starting…" : "Start Assessment"}
                  </button>
                </div>
              )}

              {!notStarted && (
                <div
                  style={{
                    background: "var(--g-card)",
                    border: "1px solid var(--g-border)",
                    borderRadius: 10,
                    padding: "16px 20px",
                    color: "var(--g-text-muted)",
                    fontSize: "0.85rem",
                  }}
                >
                  {expired
                    ? "This assessment has ended. Your labs have been shut down and your report is final."
                    : `${status.labs.length} target machine${status.labs.length !== 1 ? "s" : ""} deployed — see the Labs tab for access details, and the Report tab to write up your findings.`}
                </div>
              )}
            </>
          )}

          {section === "labs" && (
            <>
              {notStarted ? (
                <p style={{ color: "var(--g-text-muted)", fontSize: "0.85rem" }}>
                  Start the assessment from the Overview tab to deploy target machines.
                </p>
              ) : (
                <>
                  <h2
                    style={{
                      color: "var(--g-text-muted)",
                      fontSize: "0.7rem",
                      textTransform: "uppercase",
                      letterSpacing: "0.08em",
                      marginBottom: 12,
                    }}
                  >
                    Target Machines ({status.labs.length})
                  </h2>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 16, marginBottom: 8 }}>
                    {status.labs.map((lab) => (
                      <LabCard key={lab.slug} lab={lab} expired={expired} />
                    ))}
                  </div>
                </>
              )}
            </>
          )}

          {section === "report" && (
            <>
              {notStarted ? (
                <p style={{ color: "var(--g-text-muted)", fontSize: "0.85rem" }}>
                  Start the assessment from the Overview tab to unlock the report.
                </p>
              ) : (
                <ReportSection
                  content={reportContent ?? ""}
                  onChange={setReportContent}
                  alreadySubmitted={status.report_submitted}
                  expired={expired}
                />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

const outerStyle: React.CSSProperties = {
  minHeight: "100vh",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  background: "var(--g-chrome)",
  color: "var(--g-text)",
};
