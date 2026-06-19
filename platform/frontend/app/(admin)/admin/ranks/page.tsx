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
import { RankFormSheet } from "@/components/admin/ranks/RankFormSheet";

export default function AdminRanksPage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();

  const [sheetOpen, setSheetOpen] = useState(false);
  const [selected, setSelected] = useState<Rank | null>(null);

  const { data: ranks = [], isLoading } = useQuery({
    queryKey: ["admin-ranks"],
    queryFn: getAdminRanks,
  });

  function openCreate() {
    setSelected(null);
    setSheetOpen(true);
  }

  function openEdit(rank: Rank) {
    setSelected(rank);
    setSheetOpen(true);
  }

  function closeSheet() {
    setSheetOpen(false);
    setSelected(null);
  }

  const saveMutation = useMutation({
    mutationFn: (payload: { name: string; min_points: number; icon?: string; color?: string }) =>
      selected ? updateAdminRank(selected.id, payload) : createAdminRank(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-ranks"] });
      qc.invalidateQueries({ queryKey: ["ranks"] });
      push("success", selected ? "Rank updated." : "Rank created.");
      closeSheet();
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
      closeSheet();
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

      <div className="g-card" style={{ padding: 0, overflow: "hidden" }}>
        <RankTable
          ranks={ranks}
          selected={selected}
          isLoading={isLoading}
          onEdit={openEdit}
          onDelete={handleDelete}
        />
      </div>

      <RankFormSheet
        open={sheetOpen}
        initialValues={selected}
        saveMutation={saveMutation}
        onToggleActive={(rank) => toggleMutation.mutate(rank)}
        onClose={closeSheet}
      />
    </div>
  );
}
