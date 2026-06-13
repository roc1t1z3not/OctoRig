"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { X, Loader2, CheckCircle2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import type { LabTemplate } from "@/lib/api/labs";
import { startDeployment, getDeployment, type Deployment } from "@/lib/api/deployments";
import { getTeams } from "@/lib/api/teams";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useQueryClient } from "@tanstack/react-query";

interface Props {
  lab: LabTemplate;
  open: boolean;
  onClose: () => void;
}

export function StartLabDialog({ lab, open, onClose }: Props) {
  const [phase, setPhase] = useState<"confirm" | "starting" | "running" | "error">("confirm");
  const [deployment, setDeployment] = useState<Deployment | null>(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [selectedTeamId, setSelectedTeamId] = useState<number | null>(null);
  const [visibility, setVisibility] = useState<"private" | "team" | "public">("private");
  const { push } = useNotificationsStore();
  const qc = useQueryClient();
  const router = useRouter();

  const { data: teams = [] } = useQuery({
    queryKey: ["teams"],
    queryFn: getTeams,
    enabled: open,
  });

  const teamOptions = teams.filter((t) => !t.is_personal);

  useEffect(() => {
    if (!open) {
      setPhase("confirm");
      setDeployment(null);
      setErrorMsg("");
      setSelectedTeamId(null);
      setVisibility("private");
    }
  }, [open]);

  useEffect(() => {
    if (phase !== "starting" || !deployment) return;
    const interval = setInterval(async () => {
      try {
        const d = await getDeployment(deployment.id);
        setDeployment(d);
        if (d.status === "running") {
          setPhase("running");
          qc.invalidateQueries({ queryKey: ["labs"] });
          qc.invalidateQueries({ queryKey: ["deployments"] });
        } else if (d.status === "error") {
          setPhase("error");
          setErrorMsg(d.error_message ?? "Unknown error");
        }
      } catch {}
    }, 2000);
    return () => clearInterval(interval);
  }, [phase, deployment, qc]);

  async function handleStart() {
    setPhase("starting");
    try {
      const d = await startDeployment(lab.id, {
        team_id: selectedTeamId ?? undefined,
        visibility,
      });
      setDeployment(d);
      push("info", `Starting ${lab.name}…`);
    } catch (err: any) {
      setPhase("error");
      setErrorMsg(err.response?.data?.detail ?? "Failed to start lab");
    }
  }

  if (!open) return null;

  return (
    <div className="g-backdrop" onClick={onClose}>
      <div className="g-modal start-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="g-modal-header">
          <span className="font-mono text-sm">{lab.name}</span>
          <button className="g-btn g-btn-ghost g-btn-icon" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="g-modal-body">
          {phase === "confirm" && (
            <>
              <p className="text-secondary text-sm mb-1">{lab.description}</p>
              <p className="text-muted text-11">
                Network: <span className="font-mono text-accent">{lab.subnet}</span>
              </p>
              <p className="text-muted text-11">
                Containers: <span className="font-mono">{lab.container_names.join(", ")}</span>
              </p>
              {lab.requires_privileged && (
                <p className="text-warning text-11 mt-1">⚠ This lab requires --privileged mode</p>
              )}

              {/* Team + visibility options */}
              <div className="deploy-options">
                {teamOptions.length > 0 && (
                  <div className="option-row">
                    <label className="text-11 text-muted">Deploy to</label>
                    <select
                      className="g-select g-select-sm"
                      value={selectedTeamId ?? ""}
                      onChange={(e) =>
                        setSelectedTeamId(e.target.value ? Number(e.target.value) : null)
                      }
                    >
                      <option value="">Personal</option>
                      {teamOptions.map((t) => (
                        <option key={t.id} value={t.id}>{t.name}</option>
                      ))}
                    </select>
                  </div>
                )}
                <div className="option-row">
                  <label className="text-11 text-muted">Visibility</label>
                  <select
                    className="g-select g-select-sm"
                    value={visibility}
                    onChange={(e) => setVisibility(e.target.value as typeof visibility)}
                  >
                    <option value="private">Private</option>
                    {selectedTeamId && <option value="team">Team</option>}
                    <option value="public">Public (read-only)</option>
                  </select>
                </div>
              </div>
            </>
          )}

          {phase === "starting" && (
            <div className="flex items-center gap-3">
              <Loader2 size={20} className="spin text-accent" />
              <div>
                <p className="text-sm">Starting {lab.name}…</p>
                <p className="text-muted text-11">Building images and starting containers</p>
              </div>
            </div>
          )}

          {phase === "running" && deployment && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <CheckCircle2 size={18} className="text-success" />
                <span className="text-sm text-success">Lab is running</span>
              </div>
              <div className="access-info-table">
                {lab.access_info.map((row) => (
                  <div key={row.key} className="access-row">
                    <span className="text-muted text-11">{row.key}</span>
                    <span className="font-mono text-11 text-accent">{row.value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {phase === "error" && (
            <div>
              <p className="text-danger text-sm">Failed to start lab</p>
              <p className="text-muted text-11 mt-1 font-mono">{errorMsg}</p>
            </div>
          )}
        </div>

        <div className="g-modal-footer">
          {phase === "confirm" && (
            <>
              <button className="g-btn g-btn-ghost" onClick={onClose}>Cancel</button>
              <button className="g-btn g-btn-primary" onClick={handleStart}>
                Start Lab
              </button>
            </>
          )}
          {phase === "running" && (
            <>
              <button className="g-btn g-btn-ghost" onClick={onClose}>Close</button>
              <button
                className="g-btn g-btn-primary"
                onClick={() => { onClose(); router.push(`/deployments/${deployment?.id}`); }}
              >
                View Logs
              </button>
            </>
          )}
          {phase === "error" && (
            <button className="g-btn g-btn-ghost" onClick={onClose}>Close</button>
          )}
        </div>
      </div>

      <style>{`
        .start-dialog { max-width: 480px; width: 100%; }
        .spin { animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .access-info-table { display: flex; flex-direction: column; gap: 0.35rem; }
        .access-row { display: flex; justify-content: space-between; align-items: center; gap: 1rem; padding: 0.35rem 0; border-bottom: 1px solid var(--g-border); }
        .access-row:last-child { border-bottom: none; }
        .deploy-options { display: flex; flex-direction: column; gap: 0.5rem; margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--g-border); }
        .option-row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
        .flex { display: flex; }
        .items-center { align-items: center; }
        .gap-2 { gap: 0.5rem; }
        .gap-3 { gap: 0.75rem; }
        .mb-3 { margin-bottom: 0.75rem; }
        .mt-1 { margin-top: 0.25rem; }
        .mb-1 { margin-bottom: 0.25rem; }
        .text-success { color: var(--g-success); }
        .text-danger { color: var(--g-danger); }
        .text-warning { color: var(--g-warning); }
        .text-accent { color: var(--g-accent); }
      `}</style>
    </div>
  );
}
