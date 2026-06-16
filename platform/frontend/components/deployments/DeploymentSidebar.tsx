"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Clock, ExternalLink, Flag, Globe, Lock, Users } from "lucide-react";
import { CopyButton } from "@/components/ui/CopyButton";
import { type Deployment } from "@/lib/api/deployments";
import { type LabTemplate } from "@/lib/api/labs";
import { formatDateTime } from "@/lib/utils/date";

type Visibility = "private" | "team" | "public";

const VIS_ICON: Record<Visibility, React.ReactNode> = {
  private: <Lock size={11} />,
  team: <Users size={11} />,
  public: <Globe size={11} />,
};

function MetaRow({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="dd-meta-row">
      <span className="dd-meta-label">{label}</span>
      <span className={`dd-meta-value${mono ? " font-mono" : ""}`}>{value}</span>
    </div>
  );
}

interface DeploymentSidebarProps {
  deployment: Deployment;
  lab: LabTemplate | undefined;
  isActive: boolean;
  vis: Visibility;
  countdown: string;
  countdownMs: number;
  onVisibilityChange: (v: Visibility) => void;
  isChangingVisibility: boolean;
}

export function DeploymentSidebar({
  deployment,
  lab,
  isActive,
  vis,
  countdown,
  countdownMs,
  onVisibilityChange,
  isChangingVisibility,
}: DeploymentSidebarProps) {
  return (
    <div className="dd-sidebar">
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

      {deployment.dynamic_flag && (
        <div className="g-card dd-card">
          <div className="dd-section-title" style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span><Flag size={11} /> Flag</span>
            <CopyButton value={deployment.dynamic_flag!} />
          </div>
          <code className="dd-flag">{deployment.dynamic_flag}</code>
        </div>
      )}

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
          >
            {countdown}
          </div>
          <div className="dd-autodestroy-at">{formatDateTime(deployment.auto_destroy_at)}</div>
        </div>
      )}

      <div className="g-card dd-card">
        <div className="dd-section-title">Details</div>
        <div className="dd-meta-rows">
          <MetaRow label="Lab" value={deployment.lab_name} />
          <MetaRow label="Category" value={deployment.lab_category} />
          <MetaRow label="Started by" value={deployment.started_by_username} />
          {deployment.team_name && <MetaRow label="Team" value={deployment.team_name} />}
          <MetaRow label="Started" value={formatDateTime(deployment.started_at)} />
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
                <span key={c} className="g-tag text-10">{c.split("-").pop()}</span>
              ))}
            </div>
          </div>
          {lab && Object.keys(lab.exposed_ports).length > 0 && (
            <div className="dd-meta-row">
              <span className="dd-meta-label">Ports</span>
              <div className="dd-meta-chips">
                {Object.entries(lab.exposed_ports).map(([name, port]) => (
                  <span key={name} className="g-tag text-10">{name.toUpperCase()}:{port}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="g-card dd-card">
        <div className="dd-section-title">Visibility</div>
        <div className="dd-vis-pills">
          {(["private", "team", "public"] as Visibility[]).map((v) => {
            const disabled = v === "team" && !deployment.team_id;
            return (
              <button
                key={v}
                className={`dd-vis-pill${vis === v ? " dd-vis-pill--active" : ""}`}
                onClick={() => !disabled && onVisibilityChange(v)}
                disabled={disabled || isChangingVisibility}
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
        <div className="g-card dd-card">
          <div className="dd-section-title">Error</div>
          <p className="dd-error-msg font-mono">{deployment.error_message}</p>
        </div>
      )}
    </div>
  );
}
