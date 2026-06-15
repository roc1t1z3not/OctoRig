"use client";
import "./api-keys.css";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Copy, Check, Eye, EyeOff } from "lucide-react";
import { getApiKeys, createApiKey, revokeApiKey, type ApiKeyCreated } from "@/lib/api/apiKeys";
import { useNotificationsStore } from "@/stores/notifications.store";
import { formatDateTime } from "@/lib/utils/date";

export default function ApiKeysPage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const [showCreate, setShowCreate] = useState(false);
  const [newKeyName, setNewKeyName] = useState("");
  const [newKeyExpiry, setNewKeyExpiry] = useState("");
  const [createdKey, setCreatedKey] = useState<ApiKeyCreated | null>(null);
  const [copied, setCopied] = useState(false);

  const { data: keys = [], isLoading } = useQuery({
    queryKey: ["api-keys"],
    queryFn: getApiKeys,
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createApiKey({
        name: newKeyName,
        expires_at: newKeyExpiry || null,
      }),
    onSuccess: (key) => {
      qc.invalidateQueries({ queryKey: ["api-keys"] });
      setCreatedKey(key);
      setNewKeyName("");
      setNewKeyExpiry("");
      setShowCreate(false);
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to create key"),
  });

  const revokeMutation = useMutation({
    mutationFn: revokeApiKey,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["api-keys"] });
      push("success", "API key revoked");
    },
    onError: () => push("error", "Failed to revoke key"),
  });

  async function copyKey(key: string) {
    await navigator.clipboard.writeText(key);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">API Keys</h1>
        <button
          className="g-btn g-btn-primary"
          onClick={() => { setShowCreate(true); setCreatedKey(null); }}
        >
          <Plus size={14} />
          New Key
        </button>
      </div>

      {/* One-time key display */}
      {createdKey && (
        <div className="key-reveal g-panel">
          <div className="g-panel-header">
            <span className="text-success font-mono text-sm">Key created — copy it now</span>
          </div>
          <div className="key-reveal-body">
            <p className="text-muted text-11">
              This is the only time your full API key will be shown. Store it securely.
            </p>
            <div className="key-display">
              <code className="key-value font-mono text-sm">{createdKey.raw_key}</code>
              <button
                className="g-btn g-btn-ghost g-btn-icon"
                onClick={() => copyKey(createdKey.raw_key)}
                title="Copy key"
              >
                {copied ? <Check size={14} className="text-success" /> : <Copy size={14} />}
              </button>
            </div>
            <button
              className="g-btn g-btn-ghost g-btn-sm mt-2"
              onClick={() => setCreatedKey(null)}
            >
              I've saved my key
            </button>
          </div>
        </div>
      )}

      {/* Create form */}
      {showCreate && (
        <div className="create-form g-panel">
          <div className="g-panel-header">
            <span className="font-mono text-sm">New API Key</span>
          </div>
          <div className="create-body">
            <div className="field">
              <label className="text-11 text-muted">Key Name</label>
              <input
                className="g-input"
                placeholder="e.g. CI/CD Pipeline"
                value={newKeyName}
                onChange={(e) => setNewKeyName(e.target.value)}
                autoFocus
              />
            </div>
            <div className="field">
              <label className="text-11 text-muted">Expiry Date (optional)</label>
              <input
                className="g-input"
                type="datetime-local"
                value={newKeyExpiry}
                onChange={(e) => setNewKeyExpiry(e.target.value)}
              />
            </div>
            <div className="form-actions">
              <button
                className="g-btn g-btn-ghost"
                onClick={() => setShowCreate(false)}
              >
                Cancel
              </button>
              <button
                className="g-btn g-btn-primary"
                onClick={() => createMutation.mutate()}
                disabled={!newKeyName.trim() || createMutation.isPending}
              >
                {createMutation.isPending ? "Creating…" : "Create Key"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Keys list */}
      {isLoading ? (
        <div className="text-muted text-sm">Loading…</div>
      ) : keys.length === 0 ? (
        <div className="g-panel empty-state">
          <p className="text-muted text-sm">No API keys yet.</p>
          <p className="text-muted text-11">
            Create a key to authenticate via CLI, CI/CD pipelines, or external integrations.
          </p>
        </div>
      ) : (
        <div className="keys-panel g-panel">
          <table className="g-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Prefix</th>
                <th>Status</th>
                <th>Last Used</th>
                <th>Expires</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {keys.map((key) => (
                <tr key={key.id} className={!key.is_active ? "row-inactive" : ""}>
                  <td className="font-mono text-sm">{key.name}</td>
                  <td className="font-mono text-11 text-muted">oktor_{key.key_prefix}…</td>
                  <td>
                    <span className={`status-dot ${key.is_active ? "status-dot--active" : "status-dot--inactive"}`}>
                      {key.is_active ? "Active" : "Revoked"}
                    </span>
                  </td>
                  <td className="text-11 text-muted">
                    {key.last_used_at ? formatDateTime(key.last_used_at) : "Never"}
                  </td>
                  <td className="text-11 text-muted">
                    {key.expires_at ? formatDateTime(key.expires_at) : "Never"}
                  </td>
                  <td className="font-mono text-11 text-muted">
                    {formatDateTime(key.created_at)}
                  </td>
                  <td>
                    {key.is_active && (
                      <button
                        className="g-btn g-btn-danger g-btn-icon"
                        onClick={() => {
                          if (confirm("Revoke this API key? This cannot be undone.")) {
                            revokeMutation.mutate(key.id);
                          }
                        }}
                        disabled={revokeMutation.isPending}
                        title="Revoke key"
                      >
                        <Trash2 size={13} />
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
