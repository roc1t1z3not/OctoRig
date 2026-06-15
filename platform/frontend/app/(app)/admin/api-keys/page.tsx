"use client";
import "../admin.css";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Key, ShieldOff } from "lucide-react";
import { getAdminApiKeys } from "@/lib/api/admin";
import { revokeAdminApiKey } from "@/lib/api/settings";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";
import { useUserStore } from "@/stores/user.store";
import { useAdminGuard } from "@/hooks/useAdminGuard";
import { formatDateTime } from "@/lib/utils/date";

export default function AdminApiKeysPage() {
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();
  const { user } = useUserStore();
  const qc = useQueryClient();

  useAdminGuard();

  const [activeOnly, setActiveOnly] = useState(true);

  const { data: keys = [], isLoading } = useQuery({
    queryKey: ["admin-api-keys", activeOnly],
    queryFn: () => getAdminApiKeys({ active_only: activeOnly }),
    enabled: !!(user?.is_admin || user?.is_superuser),
  });

  const revokeMutation = useMutation({
    mutationFn: revokeAdminApiKey,
    onSuccess: () => {
      push("success", "API key revoked");
      qc.invalidateQueries({ queryKey: ["admin-api-keys"] });
    },
    onError: () => push("error", "Failed to revoke key"),
  });

  function handleRevoke(id: number, name: string, username: string) {
    confirm({
      title: "Revoke API key?",
      body: `Revoke "${name}" owned by ${username}? Any integrations using this key will stop working immediately.`,
      confirmLabel: "Revoke",
      dangerous: true,
      onConfirm: () => revokeMutation.mutate(id),
    });
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">
          <Key size={16} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
          API Keys
        </h1>
        <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8125rem", color: "var(--g-text-muted)", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={activeOnly}
            onChange={(e) => setActiveOnly(e.target.checked)}
          />
          Active only
        </label>
      </div>

      {isLoading ? (
        <p style={{ color: "var(--g-text-muted)", fontSize: "0.875rem" }}>Loading…</p>
      ) : keys.length === 0 ? (
        <div className="g-card" style={{ textAlign: "center", padding: "2rem", color: "var(--g-text-muted)" }}>
          No API keys found.
        </div>
      ) : (
        <div className="g-card" style={{ padding: 0, overflow: "hidden" }}>
          <table className="g-table">
            <thead>
              <tr>
                <th>Key</th>
                <th>Owner</th>
                <th>Created</th>
                <th>Last Used</th>
                <th>Expires</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {keys.map((k) => (
                <tr key={k.id} style={{ opacity: k.is_active ? 1 : 0.5 }}>
                  <td>
                    <div style={{ fontWeight: 600, fontSize: "0.8125rem", fontFamily: "monospace" }}>{k.name}</div>
                    <div style={{ fontSize: "0.6875rem", color: "var(--g-text-muted)", fontFamily: "monospace" }}>{k.key_prefix}…</div>
                  </td>
                  <td style={{ fontSize: "0.8125rem" }}>{k.username}</td>
                  <td style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>
                    {formatDateTime(k.created_at)}
                  </td>
                  <td style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>
                    {k.last_used_at ? formatDateTime(k.last_used_at) : "Never"}
                  </td>
                  <td style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>
                    {k.expires_at ? formatDateTime(k.expires_at) : "Never"}
                  </td>
                  <td>
                    <span style={{
                      fontSize: "0.6875rem", fontWeight: 700, fontFamily: "monospace",
                      textTransform: "uppercase",
                      color: k.is_active ? "var(--g-success)" : "var(--g-text-muted)",
                    }}>
                      {k.is_active ? "active" : "revoked"}
                    </span>
                  </td>
                  <td>
                    {k.is_active && (
                      <button
                        className="g-btn g-btn-danger g-btn-sm"
                        disabled={revokeMutation.isPending}
                        onClick={() => handleRevoke(k.id, k.name, k.username)}
                      >
                        <ShieldOff size={12} />
                        Revoke
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
