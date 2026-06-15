"use client";
import "./ranks-admin.css";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Trash2, X } from "lucide-react";
import {
  getAdminRanks,
  createAdminRank,
  updateAdminRank,
  deleteAdminRank,
  type Rank,
} from "@/lib/api/ranks";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";

const EMPTY_FORM = { name: "", min_points: 0, icon: "", color: "#6b7280" };

export default function AdminRanksPage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();

  const [selected, setSelected] = useState<Rank | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);

  const { data: ranks = [], isLoading } = useQuery({
    queryKey: ["admin-ranks"],
    queryFn: getAdminRanks,
  });

  function openCreate() {
    setSelected(null);
    setForm(EMPTY_FORM);
  }

  function openEdit(rank: Rank) {
    setSelected(rank);
    setForm({
      name: rank.name,
      min_points: rank.min_points,
      icon: rank.icon ?? "",
      color: rank.color ?? "#6b7280",
    });
  }

  function closePanel() {
    setSelected(null);
    setForm(EMPTY_FORM);
  }

  const saveMutation = useMutation({
    mutationFn: () => {
      const payload = {
        name: form.name,
        min_points: form.min_points,
        icon: form.icon || undefined,
        color: form.color || undefined,
      };
      return selected
        ? updateAdminRank(selected.id, payload)
        : createAdminRank(payload);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-ranks"] });
      qc.invalidateQueries({ queryKey: ["ranks"] });
      push("success", selected ? "Rank updated." : "Rank created.");
      closePanel();
    },
    onError: () => push("error", "Failed to save rank."),
  });

  const toggleMutation = useMutation({
    mutationFn: (rank: Rank) =>
      updateAdminRank(rank.id, { is_active: !rank.is_active }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-ranks"] });
      qc.invalidateQueries({ queryKey: ["ranks"] });
    },
    onError: () => push("error", "Failed to update rank."),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteAdminRank(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-ranks"] });
      qc.invalidateQueries({ queryKey: ["ranks"] });
      push("success", "Rank deleted.");
      closePanel();
    },
    onError: () => push("error", "Failed to delete rank."),
  });

  function handleDelete(rank: Rank) {
    confirm({
      title: "Delete rank",
      body: `Delete "${rank.name}"? Users currently at this rank will drop to the one below.`,
      confirmLabel: "Delete",
      dangerous: true,
      onConfirm: () => deleteMutation.mutate(rank.id),
    });
  }

  const isEditing = selected !== null;
  const isPanelOpen = isEditing || form !== EMPTY_FORM;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title font-mono">Ranks</h1>
          <p className="page-sub">{ranks.length} ranks configured</p>
        </div>
        <button className="g-btn g-btn-primary" onClick={openCreate}>
          <Plus size={13} />
          New Rank
        </button>
      </div>

      <div className="ranks-grid">
        {/* Table */}
        <div className="g-card" style={{ padding: 0, overflow: "hidden" }}>
          {isLoading ? (
            <div className="text-muted text-sm" style={{ padding: "1rem" }}>Loading…</div>
          ) : (
            <table className="rank-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Icon</th>
                  <th>Min Points</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {ranks.map((rank) => (
                  <tr
                    key={rank.id}
                    className={selected?.id === rank.id ? "selected" : ""}
                    style={{ cursor: "pointer" }}
                    onClick={() => openEdit(rank)}
                  >
                    <td>
                      <span
                        className="rank-chip-preview"
                        style={{
                          color: rank.color ?? "var(--g-text-muted)",
                          borderColor: rank.color ?? "var(--g-border)",
                        }}
                      >
                        <span className="color-swatch" style={{ background: rank.color ?? "#6b7280" }} />
                        {rank.name}
                      </span>
                    </td>
                    <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem" }}>{rank.icon || "—"}</td>
                    <td className="rank-pts">{rank.min_points.toLocaleString()}</td>
                    <td>
                      <span
                        className="inactive-pill"
                        style={rank.is_active ? { background: "var(--g-accent-dim)", color: "var(--g-accent)" } : undefined}
                      >
                        {rank.is_active ? "active" : "inactive"}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: "0.4rem" }} onClick={(e) => e.stopPropagation()}>
                        <button
                          className="g-btn g-btn-ghost"
                          style={{ padding: "0.2rem 0.4rem" }}
                          onClick={() => openEdit(rank)}
                          title="Edit"
                        >
                          <Pencil size={12} />
                        </button>
                        <button
                          className="g-btn g-btn-ghost"
                          style={{ padding: "0.2rem 0.4rem", color: "var(--g-danger)" }}
                          onClick={() => handleDelete(rank)}
                          title="Delete"
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Form panel — always visible so user can create */}
        <div className="g-card">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h2 className="font-mono" style={{ fontSize: "0.85rem" }}>
              {isEditing ? `Edit "${selected!.name}"` : "New Rank"}
            </h2>
            {isEditing && (
              <button className="g-btn g-btn-ghost" onClick={closePanel} style={{ padding: "0.2rem" }}>
                <X size={14} />
              </button>
            )}
          </div>

          {/* Live preview */}
          <div style={{ marginBottom: "1rem" }}>
            <span
              className="rank-chip-preview"
              style={{
                color: form.color || "var(--g-text-muted)",
                borderColor: form.color || "var(--g-border)",
                fontSize: "0.75rem",
              }}
            >
              {form.name || "Rank name"}
            </span>
          </div>

          <div className="rank-form">
            <label>
              Name
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                placeholder="e.g. Hacker"
              />
            </label>

            <label>
              Min Points
              <input
                type="number"
                value={form.min_points}
                onChange={(e) => setForm((f) => ({ ...f, min_points: Number(e.target.value) }))}
                min={0}
              />
            </label>

            <label>
              Icon (lucide name)
              <input
                type="text"
                value={form.icon}
                onChange={(e) => setForm((f) => ({ ...f, icon: e.target.value }))}
                placeholder="e.g. terminal, skull, crown"
              />
            </label>

            <label>
              Color
              <div className="color-row">
                <input
                  type="color"
                  value={form.color}
                  onChange={(e) => setForm((f) => ({ ...f, color: e.target.value }))}
                />
                <input
                  type="text"
                  value={form.color}
                  onChange={(e) => setForm((f) => ({ ...f, color: e.target.value }))}
                  placeholder="#6b7280"
                  style={{ flex: 1 }}
                />
              </div>
            </label>

            {isEditing && (
              <label style={{ flexDirection: "row", alignItems: "center", gap: "0.5rem" }}>
                <input
                  type="checkbox"
                  checked={selected!.is_active}
                  onChange={() => toggleMutation.mutate(selected!)}
                />
                Active
              </label>
            )}

            <div className="rank-form-actions">
              <button
                className="g-btn g-btn-primary"
                onClick={() => saveMutation.mutate()}
                disabled={!form.name || saveMutation.isPending}
              >
                {saveMutation.isPending ? "Saving…" : isEditing ? "Save Changes" : "Create Rank"}
              </button>
              {isEditing && (
                <button
                  className="g-btn g-btn-ghost"
                  style={{ color: "var(--g-danger)" }}
                  onClick={() => handleDelete(selected!)}
                >
                  <Trash2 size={12} />
                  Delete
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
