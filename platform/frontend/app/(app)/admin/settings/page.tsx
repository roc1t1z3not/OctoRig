"use client";
import "../admin.css";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { AlertTriangle, RotateCcw } from "lucide-react";
import { resetDatabase } from "@/lib/api/admin";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";
import { useUserStore } from "@/stores/user.store";
import { useEffect } from "react";

export default function AdminSettingsPage() {
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();
  const { user } = useUserStore();
  const router = useRouter();

  useEffect(() => {
    if (user && !user.is_admin && !user.is_superuser) router.replace("/");
  }, [user, router]);

  const resetDbMutation = useMutation({
    mutationFn: resetDatabase,
    onSuccess: () => push("success", "Database reset — all activity data cleared"),
    onError: () => push("error", "Failed to reset database"),
  });

  function handleResetDb() {
    confirm({
      title: "Reset entire database?",
      body: "This will permanently delete ALL challenge submissions, scores, hint unlocks, deployments, and audit logs for every user. Lab templates, challenges, and accounts are kept. This cannot be undone.",
      confirmLabel: "Reset Database",
      dangerous: true,
      onConfirm: () => resetDbMutation.mutate(),
    });
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Settings</h1>
      </div>

      {/* ── DANGER ZONE ─────────────────────────────────────────────── */}
      <div className="danger-zone">
        <div className="danger-zone-header">
          <AlertTriangle size={14} />
          <span>Danger Zone</span>
        </div>

        <div className="danger-action">
          <div className="danger-action-info">
            <span className="danger-action-title">Reset Database</span>
            <span className="danger-action-desc">
              Wipe all user activity — submissions, scores, hint unlocks, deployments, and audit logs.
              Accounts, teams, labs, and challenges are preserved.
            </span>
          </div>
          <button
            className="g-btn g-btn-danger"
            disabled={resetDbMutation.isPending}
            onClick={handleResetDb}
          >
            <RotateCcw size={13} />
            {resetDbMutation.isPending ? "Resetting…" : "Reset Database"}
          </button>
        </div>
      </div>

      <style>{`
        .danger-zone {
          border: 1px solid var(--g-danger);
          border-radius: 8px;
          overflow: hidden;
          margin-top: 1.5rem;
        }
        .danger-zone-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.625rem 1rem;
          background: color-mix(in srgb, var(--g-danger) 10%, transparent);
          color: var(--g-danger);
          font-size: 0.6875rem;
          font-weight: 700;
          font-family: var(--font-mono, monospace);
          text-transform: uppercase;
          letter-spacing: 0.08em;
          border-bottom: 1px solid color-mix(in srgb, var(--g-danger) 30%, transparent);
        }
        .danger-action {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1.5rem;
          padding: 1rem 1rem;
        }
        .danger-action-info {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        .danger-action-title {
          font-size: 0.8125rem;
          font-weight: 600;
          color: var(--g-text);
        }
        .danger-action-desc {
          font-size: 0.75rem;
          color: var(--g-text-muted);
          line-height: 1.5;
          max-width: 480px;
        }
      `}</style>
    </div>
  );
}
