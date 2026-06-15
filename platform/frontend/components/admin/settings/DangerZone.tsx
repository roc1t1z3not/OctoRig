import { AlertTriangle, RotateCcw } from "lucide-react";

export function DangerZone({
  onResetDb,
  isPending,
}: {
  onResetDb: () => void;
  isPending: boolean;
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
    </div>
  );
}
