"use client";
import "./deployment-detail.css";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Square, Globe, Lock, Users, Clock } from "lucide-react";
import Link from "next/link";
import {
  getDeployment,
  stopDeployment,
  setDeploymentVisibility,
  type Deployment,
} from "@/lib/api/deployments";
import { createScheduledAction } from "@/lib/api/scheduler";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import { LogViewer } from "@/components/deployments/LogViewer";
import { useNotificationsStore } from "@/stores/notifications.store";

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

function addHours(h: number): string {
  const d = new Date(Date.now() + h * 3600_000);
  // datetime-local input format: yyyy-MM-ddTHH:mm
  return d.toISOString().slice(0, 16);
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

  if (isLoading) return <div className="page text-muted text-sm">Loading…</div>;
  if (!deployment) return <div className="page text-muted text-sm">Deployment not found.</div>;

  const canStop = deployment.status === "running" || deployment.status === "error";
  const canSchedule = deployment.status === "running";
  const vis = (deployment.visibility ?? "private") as Visibility;

  return (
    <div className="page deployment-page">
      {/* Header */}
      <div className="deployment-header">
        <Link href="/deployments" className="g-btn g-btn-ghost g-btn-icon" title="Back">
          <ArrowLeft size={16} />
        </Link>
        <h1 className="page-title font-mono">{deployment.lab_name}</h1>
        <DeploymentStatusBadge status={deployment.status} />
        <div className="header-actions">
          {canSchedule && (
            <button
              className="g-btn g-btn-ghost g-btn-sm"
              onClick={() => { setShowSchedule(true); setScheduledAt(addHours(2)); }}
            >
              <Clock size={13} />
              Schedule Destroy
            </button>
          )}
          {canStop && (
            <button
              className="g-btn g-btn-danger"
              onClick={() => stopMutation.mutate()}
              disabled={stopMutation.isPending}
            >
              <Square size={14} />
              Stop
            </button>
          )}
        </div>
      </div>

      {/* Schedule destroy modal */}
      {showSchedule && (
        <div className="g-backdrop" onClick={() => setShowSchedule(false)}>
          <div className="g-modal schedule-modal" onClick={(e) => e.stopPropagation()}>
            <div className="g-modal-header">
              <span className="font-mono text-sm">Schedule Destroy — {deployment.lab_name}</span>
            </div>
            <div className="g-modal-body">
              <p className="text-muted text-11 mb-2">
                The lab will be automatically stopped at the specified time.
              </p>
              <div className="preset-row">
                {PRESETS.map((p) => (
                  <button
                    key={p.label}
                    className="g-btn g-btn-ghost g-btn-sm preset-btn"
                    onClick={() => setScheduledAt(addHours(p.hours))}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
              <div className="field mt-2">
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

      {/* Body: metadata + logs */}
      <div className="deployment-body">
        {/* Meta panel */}
        <div className="g-panel meta-panel">
          <Row label="Lab" value={deployment.lab_name} />
          <Row label="Category" value={deployment.lab_category} />
          <Row label="Started By" value={deployment.started_by_username} />
          {deployment.team_name && <Row label="Team" value={deployment.team_name} />}
          <Row
            label="Started At"
            value={deployment.started_at ? new Date(deployment.started_at).toLocaleString() : "—"}
          />
          {deployment.stopped_at && (
            <Row label="Stopped At" value={new Date(deployment.stopped_at).toLocaleString()} />
          )}
          <Row label="Containers" value={deployment.container_names.join(", ")} mono />

          {/* Visibility picker */}
          <div className="vis-section">
            <span className="text-muted text-11">Visibility</span>
            <div className="vis-pills">
              {(["private", "team", "public"] as Visibility[]).map((v) => {
                const disabled = v === "team" && !deployment.team_id;
                return (
                  <button
                    key={v}
                    className={`vis-pill ${vis === v ? "vis-pill--active" : ""}`}
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

          {deployment.error_message && (
            <div className="mt-2">
              <span className="text-11 text-muted">Error</span>
              <p className="font-mono text-11 text-danger mt-1">{deployment.error_message}</p>
            </div>
          )}
        </div>

        {/* Log viewer */}
        <div className="log-panel g-panel">
          <LogViewer
            deploymentId={deploymentId}
            containerNames={deployment.container_names}
          />
        </div>
      </div>
    </div>
  );
}

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="meta-row">
      <span className="text-muted text-11">{label}</span>
      <span className={mono ? "font-mono text-11 text-secondary" : "text-sm text-secondary"}>
        {value}
      </span>
    </div>
  );
}
