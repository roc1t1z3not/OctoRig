"use client";
import "../deployment-detail.css";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft, CheckCircle2, Clock, ExternalLink,
  Flag, Globe, Lock, RotateCcw, Square, Target, Users,
} from "lucide-react";
import { CopyButton } from "@/components/ui/CopyButton";
import Link from "next/link";
import {
  getDeployment,
  resetDeployment,
  setDeploymentVisibility,
  stopDeployment,
  type Deployment,
} from "@/lib/api/deployments";
import { getLabs, type LabTemplate } from "@/lib/api/labs";
import {
  getChallenges,
  type ChallengeListItem,
  type ChallengeDifficulty,
} from "@/lib/api/challenges";
import { createScheduledAction } from "@/lib/api/scheduler";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import { formatDateTime } from "@/lib/utils/date";
import { LabCategoryBadge } from "@/components/labs/LabCategoryBadge";
import { LogViewer } from "@/components/deployments/LogViewer";
import { useNotificationsStore } from "@/stores/notifications.store";
import { PageSpinner } from "@/components/ui/Spinner";

type Visibility = "private" | "team" | "public";

const VIS_ICON: Record<Visibility, React.ReactNode> = {
  private: <Lock size={11} />,
  team: <Users size={11} />,
  public: <Globe size={11} />,
};

const PRESETS: { label: string; hours: number }[] = [
  { label: "2 h", hours: 2 },
  { label: "24 h", hours: 24 },
  { label: "7 d", hours: 168 },
];

const DIFF_COLOR: Record<ChallengeDifficulty, string> = {
  easy: "dd-diff-easy",
  medium: "dd-diff-medium",
  hard: "dd-diff-hard",
  insane: "dd-diff-insane",
};

function addHours(h: number): string {
  return new Date(Date.now() + h * 3_600_000).toISOString().slice(0, 16);
}

function useCountdown(isoTarget: string | null): { label: string; remainingMs: number } {
  const [state, setState] = useState({ label: "", remainingMs: Infinity });
  useEffect(() => {
    if (!isoTarget) return;
    const tick = () => {
      const diff = new Date(isoTarget).getTime() - Date.now();
      if (diff <= 0) { setState({ label: "Expired", remainingMs: 0 }); return; }
      const h = Math.floor(diff / 3_600_000);
      const m = Math.floor((diff % 3_600_000) / 60_000);
      const s = Math.floor((diff % 60_000) / 1_000);
      setState({ label: h > 0 ? `${h}h ${m}m` : `${m}m ${s}s`, remainingMs: diff });
    };
    tick();
    const id = setInterval(tick, 1_000);
    return () => clearInterval(id);
  }, [isoTarget]);
  return state;
}

function DiffBadge({ difficulty }: { difficulty: ChallengeDifficulty }) {
  return (
    <span className={`dd-diff-badge ${DIFF_COLOR[difficulty]}`}>{difficulty}</span>
  );
}

function MetaRow({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="dd-meta-row">
      <span className="dd-meta-label">{label}</span>
      <span className={`dd-meta-value${mono ? " font-mono" : ""}`}>{value}</span>
    </div>
  );
}

export default function DeploymentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const deploymentId = Number(id);
  const qc = useQueryClient();
  const { push } = useNotificationsStore();

  const [showSchedule, setShowSchedule] = useState(false);
  const [scheduledAt, setScheduledAt] = useState(() => addHours(2));

  const { data: deployment, isLoading } = useQuery({
    queryKey: ["deployment", deploymentId],
    queryFn: () => getDeployment(deploymentId),
  });

  const { data: labs = [] } = useQuery<LabTemplate[]>({
    queryKey: ["labs"],
    queryFn: () => getLabs(),
    staleTime: 30_000,
    enabled: !!deployment,
  });

  const lab = deployment ? labs.find((l) => l.slug === deployment.lab_slug) : undefined;

  const { data: challenges = [] } = useQuery({
    queryKey: ["challenges", { lab_slug: deployment?.lab_slug }],
    queryFn: () => getChallenges({ lab_slug: deployment!.lab_slug }),
    enabled: !!deployment?.lab_slug,
  });

  const stopMutation = useMutation({
    mutationFn: () => stopDeployment(deploymentId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["deployment", deploymentId] });
      qc.invalidateQueries({ queryKey: ["deployments"] });
      qc.invalidateQueries({ queryKey: ["labs"] });
      push("success", "Lab stop requested");
    },
    onError: () => push("error", "Failed to stop lab"),
  });

  const resetMutation = useMutation({
    mutationFn: () => resetDeployment(deploymentId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["deployment", deploymentId] });
      push("success", "Lab reset requested");
    },
    onError: () => push("error", "Failed to reset lab"),
  });

  const visMutation = useMutation({
    mutationFn: (v: Visibility) => setDeploymentVisibility(deploymentId, v),
    onSuccess: (updated) => {
      qc.setQueryData(["deployment", deploymentId], updated);
      push("success", `Visibility set to ${updated.visibility}`);
    },
    onError: () => push("error", "Failed to update visibility"),
  });

  const scheduleMutation = useMutation({
    mutationFn: () =>
      createScheduledAction({
        action: "destroy",
        deployment_id: deploymentId,
        scheduled_at: new Date(scheduledAt).toISOString(),
      }),
    onSuccess: () => {
      setShowSchedule(false);
      push("success", "Destroy scheduled");
    },
    onError: (err: any) =>
      push("error", err?.response?.data?.detail ?? "Failed to schedule destroy"),
  });

  const { label: countdown, remainingMs: countdownMs } = useCountdown(deployment?.auto_destroy_at ?? null);

  if (isLoading) return <div className="page"><PageSpinner /></div>;
  if (!deployment) return <div className="page text-muted text-sm">Deployment not found.</div>;

  const isActive = deployment.status === "running" || deployment.status === "starting";
  const canStop = deployment.status === "running" || deployment.status === "error";
  const canReset = deployment.status === "running" && deployment.lab_category === "firerange";
  const canSchedule = deployment.status === "running";
  const vis = (deployment.visibility ?? "private") as Visibility;

  const labUrl = lab?.access_info.find((a) => a.key === "URL")?.value;

  return (
    <div className="page">
      <Link href="/deployments" className="dd-back-link">
        <ArrowLeft size={14} /> Deployments
      </Link>

      {/* ── Header ── */}
      <div className="dd-header">
        <div className="dd-title-row">
          <h1 className="dd-title font-mono">{deployment.lab_name}</h1>
          <div className="dd-badges">
            <DeploymentStatusBadge status={deployment.status} />
            <LabCategoryBadge category={deployment.lab_category} />
          </div>
        </div>

        {lab?.description && <p className="dd-desc">{lab.description}</p>}

        <div className="dd-controls">
          {canStop && (
            <button
              className="g-btn g-btn-danger"
              onClick={() => stopMutation.mutate()}
              disabled={stopMutation.isPending || deployment.status === "stopping"}
            >
              <Square size={14} /> Stop
            </button>
          )}
          {canReset && (
            <button
              className="g-btn g-btn-ghost"
              onClick={() => resetMutation.mutate()}
              disabled={resetMutation.isPending}
            >
              <RotateCcw size={14} /> Reset
            </button>
          )}
          {labUrl && isActive && (
            <a href={labUrl} target="_blank" rel="noopener noreferrer" className="g-btn g-btn-ghost">
              <ExternalLink size={14} /> Open Lab
            </a>
          )}
          {canSchedule && (
            <button
              className="g-btn g-btn-ghost g-btn-sm"
              onClick={() => { setShowSchedule(true); setScheduledAt(addHours(2)); }}
            >
              <Clock size={13} /> Schedule Destroy
            </button>
          )}
        </div>
      </div>

      {/* ── Body: logs + sidebar ── */}
      <div className="dd-body">
        {/* Log viewer */}
        <div className="dd-logs g-panel">
          <LogViewer
            deploymentId={deploymentId}
            containerNames={deployment.container_names}
          />
        </div>

        {/* Sidebar */}
        <div className="dd-sidebar">
          {/* Access info — only when running */}
          {isActive && lab && lab.access_info.length > 0 && (
            <div className="g-card dd-card">
              <div className="dd-section-title">Access</div>
              <div className="dd-access-rows">
                {lab.access_info.map((row) => (
                  <div key={row.key} className="dd-access-row">
                    <span className="dd-access-key">{row.key}</span>
                    <span className="dd-access-val font-mono">{row.value}</span>
                    <CopyButton value={row.value} />
                    {(row.key === "URL" || row.value.startsWith("http")) && (
                      <a href={row.value} target="_blank" rel="noopener noreferrer" className="dd-access-link">
                        <ExternalLink size={11} />
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Dynamic flag — challenge instance deployments */}
          {deployment.dynamic_flag && (
            <div className="g-card dd-card">
              <div className="dd-section-title" style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span><Flag size={11} /> Flag</span>
                <CopyButton value={deployment.dynamic_flag!} />
              </div>
              <code className="dd-flag">{deployment.dynamic_flag}</code>
            </div>
          )}

          {/* Auto-destroy countdown */}
          {deployment.auto_destroy_at && countdown && (
            <div className="g-card dd-card">
              <div className="dd-section-title"><Clock size={11} /> Auto Destroy</div>
              <div
                className="dd-countdown"
                style={{
                  color: countdownMs <= 15 * 60_000
                    ? "var(--g-danger)"
                    : countdownMs <= 60 * 60_000
                    ? "var(--g-warning)"
                    : undefined,
                }}
              >{countdown}</div>
              <div className="dd-autodestroy-at">
                {formatDateTime(deployment.auto_destroy_at)}
              </div>
            </div>
          )}

          {/* Deployment metadata */}
          <div className="g-card dd-card">
            <div className="dd-section-title">Details</div>
            <div className="dd-meta-rows">
              <MetaRow label="Lab" value={deployment.lab_name} />
              <MetaRow label="Category" value={deployment.lab_category} />
              <MetaRow label="Started by" value={deployment.started_by_username} />
              {deployment.team_name && (
                <MetaRow label="Team" value={deployment.team_name} />
              )}
              <MetaRow
                label="Started"
                value={formatDateTime(deployment.started_at)}
              />
              {deployment.stopped_at && (
                <MetaRow label="Stopped" value={formatDateTime(deployment.stopped_at)} />
              )}
              {lab && (
                <>
                  <MetaRow label="Subnet" value={lab.subnet} mono />
                  <MetaRow label="App IP" value={lab.app_ip} mono />
                </>
              )}
              <div className="dd-meta-row">
                <span className="dd-meta-label">Containers</span>
                <div className="dd-meta-chips">
                  {deployment.container_names.map((c) => (
                    <span key={c} className="g-tag text-10">
                      {c.split("-").pop()}
                    </span>
                  ))}
                </div>
              </div>
              {lab && Object.keys(lab.exposed_ports).length > 0 && (
                <div className="dd-meta-row">
                  <span className="dd-meta-label">Ports</span>
                  <div className="dd-meta-chips">
                    {Object.entries(lab.exposed_ports).map(([name, port]) => (
                      <span key={name} className="g-tag text-10">
                        {name.toUpperCase()}:{port}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Visibility */}
          <div className="g-card dd-card">
            <div className="dd-section-title">Visibility</div>
            <div className="dd-vis-pills">
              {(["private", "team", "public"] as Visibility[]).map((v) => {
                const disabled = v === "team" && !deployment.team_id;
                return (
                  <button
                    key={v}
                    className={`dd-vis-pill${vis === v ? " dd-vis-pill--active" : ""}`}
                    onClick={() => !disabled && visMutation.mutate(v)}
                    disabled={disabled || visMutation.isPending}
                    title={disabled ? "Assign a team first" : undefined}
                  >
                    {VIS_ICON[v]}
                    {v.charAt(0).toUpperCase() + v.slice(1)}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Error message */}
          {deployment.error_message && (
            <div className="g-card dd-card">
              <div className="dd-section-title">Error</div>
              <p className="dd-error-msg font-mono">{deployment.error_message}</p>
            </div>
          )}
        </div>
      </div>

      {/* ── Challenges (full-width below columns) ── */}
      {challenges.length > 0 && (
        <div className="g-card dd-challenges">
          <div className="dd-section-title">
            Challenges
            <span className="dd-ch-count">{challenges.length}</span>
          </div>
          <div className="dd-ch-list">
            {challenges.map((ch) => (
              <Link key={ch.id} href={`/challenges/${ch.slug}`} className="dd-ch-row">
                <div className="dd-ch-info">
                  <span className="dd-ch-cat">{ch.category.replace("-", " ")}</span>
                  <span className="dd-ch-title">{ch.title}</span>
                  <div className="dd-ch-tags">
                    {ch.tags.slice(0, 4).map((t) => (
                      <span key={t} className="g-tag text-10">{t}</span>
                    ))}
                  </div>
                </div>
                <div className="dd-ch-right">
                  <DiffBadge difficulty={ch.difficulty} />
                  <span className="dd-ch-pts">{ch.points} pts</span>
                  <div className="dd-ch-meta">
                    {ch.estimated_minutes && (
                      <span className="dd-ch-meta-item">
                        <Clock size={10} />{ch.estimated_minutes}m
                      </span>
                    )}
                    <span className="dd-ch-meta-item">
                      <Target size={10} />{ch.solve_count}
                    </span>
                    {ch.solved_by_me && (
                      <span className="dd-ch-solved">
                        <CheckCircle2 size={10} />Solved
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* ── Schedule destroy modal ── */}
      {showSchedule && (
        <div className="g-backdrop" onClick={() => setShowSchedule(false)}>
          <div className="g-modal" onClick={(e) => e.stopPropagation()}>
            <div className="g-modal-header">
              <span className="font-mono text-sm">
                Schedule Destroy — {deployment.lab_name}
              </span>
            </div>
            <div className="g-modal-body">
              <p className="text-muted text-11" style={{ marginBottom: "0.75rem" }}>
                The lab will be automatically stopped at the specified time.
              </p>
              <div className="dd-preset-row">
                {PRESETS.map((p) => (
                  <button
                    key={p.label}
                    className="g-btn g-btn-ghost g-btn-sm"
                    onClick={() => setScheduledAt(addHours(p.hours))}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                <label className="text-11 text-muted">Custom time</label>
                <input
                  type="datetime-local"
                  className="g-input"
                  value={scheduledAt}
                  min={addHours(0)}
                  onChange={(e) => setScheduledAt(e.target.value)}
                />
              </div>
            </div>
            <div className="g-modal-footer">
              <button className="g-btn g-btn-ghost" onClick={() => setShowSchedule(false)}>
                Cancel
              </button>
              <button
                className="g-btn g-btn-danger"
                onClick={() => scheduleMutation.mutate()}
                disabled={scheduleMutation.isPending}
              >
                {scheduleMutation.isPending ? "Scheduling…" : "Schedule Destroy"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
