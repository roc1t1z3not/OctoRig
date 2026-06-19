// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { AlertTriangle, Power, RotateCcw } from "lucide-react";

export function DangerZone({
  onResetDb,
  isPending,
  onRestartPlatform,
  isRestartPending,
}: {
  onResetDb: () => void;
  isPending: boolean;
  onRestartPlatform: () => void;
  isRestartPending: boolean;
}) {
  return (
    <div className="danger-zone">
      <div className="danger-zone-header">
        <AlertTriangle size={14} />
        <span>Danger Zone</span>
      </div>
      <div className="danger-action">
        <div className="danger-action-info">
          <span className="danger-action-title">Reset Database</span>
          <span className="danger-action-desc">
            Wipe all user activity — submissions, scores, hint unlocks, deployments, and audit
            logs. Accounts, teams, labs, and challenges are preserved.
          </span>
        </div>
        <button
          className="g-btn g-btn-danger"
          disabled={isPending}
          onClick={onResetDb}
        >
          <RotateCcw size={13} />
          {isPending ? "Resetting…" : "Reset Database"}
        </button>
      </div>
      <div className="danger-action">
        <div className="danger-action-info">
          <span className="danger-action-title">Restart Platform</span>
          <span className="danger-action-desc">
            Stops every running lab, then restarts the API, worker, and frontend containers.
            The platform will be briefly unreachable while it comes back up.
          </span>
        </div>
        <button
          className="g-btn g-btn-danger"
          disabled={isRestartPending}
          onClick={onRestartPlatform}
        >
          <Power size={13} />
          {isRestartPending ? "Restarting…" : "Restart Platform"}
        </button>
      </div>
    </div>
  );
}
