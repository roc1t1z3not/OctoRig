"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./api-keys.css";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, KeyRound } from "lucide-react";
import { getApiKeys, createApiKey, revokeApiKey, type ApiKeyCreated } from "@/lib/api/apiKeys";
import { useNotificationsStore } from "@/stores/notifications.store";
import { KeyReveal } from "@/components/api-keys/KeyReveal";
import { CreateKeyForm } from "@/components/api-keys/CreateKeyForm";
import { KeysTable } from "@/components/api-keys/KeysTable";

export default function ApiKeysPage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const [showCreate, setShowCreate] = useState(false);
  const [createdKey, setCreatedKey] = useState<ApiKeyCreated | null>(null);

  const { data: keys = [], isLoading } = useQuery({
    queryKey: ["api-keys"],
    queryFn: getApiKeys,
  });

  const createMutation = useMutation({
    mutationFn: (payload: { name: string; expires_at: string | null }) =>
      createApiKey(payload),
    onSuccess: (key) => {
      qc.invalidateQueries({ queryKey: ["api-keys"] });
      setCreatedKey(key);
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

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">
          <KeyRound size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
          API Keys
        </h1>
        <button
          className="g-btn g-btn-primary"
          onClick={() => { setShowCreate(true); setCreatedKey(null); }}
        >
          <Plus size={14} />
          New Key
        </button>
      </div>

      {createdKey && (
        <KeyReveal createdKey={createdKey} onDismiss={() => setCreatedKey(null)} />
      )}

      {showCreate && (
        <CreateKeyForm
          onSubmit={(name, expiry) =>
            createMutation.mutate({ name, expires_at: expiry || null })
          }
          isPending={createMutation.isPending}
          onCancel={() => setShowCreate(false)}
        />
      )}

      {isLoading ? (
        <div className="text-muted text-sm">Loading…</div>
      ) : (
        <KeysTable
          keys={keys}
          onRevoke={(id) => revokeMutation.mutate(id)}
          isPending={revokeMutation.isPending}
        />
      )}
    </div>
  );
}
