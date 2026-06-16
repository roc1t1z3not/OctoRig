"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./ranks-admin.css";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import {
  getAdminRanks,
  createAdminRank,
  updateAdminRank,
  deleteAdminRank,
  type Rank,
} from "@/lib/api/ranks";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";
import { RankTable } from "@/components/admin/ranks/RankTable";
import { RankForm, EMPTY_RANK_FORM, type RankFormState } from "@/components/admin/ranks/RankForm";

export default function AdminRanksPage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();

  const [selected, setSelected] = useState<Rank | null>(null);
  const [form, setForm] = useState<RankFormState>(EMPTY_RANK_FORM);

  const { data: ranks = [], isLoading } = useQuery({
    queryKey: ["admin-ranks"],
    queryFn: getAdminRanks,
  });

  function openCreate() {
    setSelected(null);
    setForm(EMPTY_RANK_FORM);
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
    setForm(EMPTY_RANK_FORM);
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
    mutationFn: (rank: Rank) => updateAdminRank(rank.id, { is_active: !rank.is_active }),
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
        <div className="g-card" style={{ padding: 0, overflow: "hidden" }}>
          <RankTable
            ranks={ranks}
            selected={selected}
            isLoading={isLoading}
            onEdit={openEdit}
            onDelete={handleDelete}
          />
        </div>

        <RankForm
          selected={selected}
          form={form}
          onChange={(patch) => setForm((f) => ({ ...f, ...patch }))}
          onSave={() => saveMutation.mutate()}
          onToggleActive={(rank) => toggleMutation.mutate(rank)}
          onDelete={handleDelete}
          onClose={closePanel}
          isPending={saveMutation.isPending}
        />
      </div>
    </div>
  );
}
