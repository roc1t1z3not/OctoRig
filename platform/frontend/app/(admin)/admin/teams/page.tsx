"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./teams-admin.css";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Pencil, Trash2 } from "lucide-react";
import { SearchBar } from "@/components/ui/SearchBar";
import { getAdminTeams, type AdminTeam } from "@/lib/api/admin";
import { updateTeam, deleteTeam } from "@/lib/api/teams";
import { LoadingCell, EmptyCell } from "@/components/ui/TableStates";
import { formatDateTime } from "@/lib/utils/date";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";
import { TeamEditSheet } from "@/components/admin/teams/TeamEditSheet";

const ACTION_ICON_SIZE = 16;

export default function AdminTeamsPage() {
  const [search, setSearch] = useState("");
  const [editing, setEditing] = useState<AdminTeam | null>(null);
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();

  const { data: teams = [], isLoading } = useQuery({
    queryKey: ["admin-teams", search],
    queryFn: () => getAdminTeams({ search: search || undefined }),
  });

  const updateMutation = useMutation({
    mutationFn: (payload: { name: string }) => updateTeam(editing!.id, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-teams"] });
      push("success", "Team updated.");
      setEditing(null);
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to update team."),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteTeam(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-teams"] });
      push("success", "Team deleted.");
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to delete team."),
  });

  function handleDelete(t: AdminTeam) {
    confirm({
      title: "Delete team",
      body: `Delete "${t.name}"? This removes all memberships and cannot be undone.`,
      confirmLabel: "Delete",
      dangerous: true,
      onConfirm: () => deleteMutation.mutate(t.id),
    });
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Teams</h1>
        <SearchBar value={search} onChange={setSearch} placeholder="Search teams…" />
      </div>

      <div className="g-panel">
        {isLoading ? (
          <LoadingCell />
        ) : teams.length === 0 ? (
          <EmptyCell label="No teams found." />
        ) : (
          <table className="g-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Slug</th>
                <th>Owner</th>
                <th>Members</th>
                <th>Deployments</th>
                <th>Personal</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {teams.map((t) => (
                <tr key={t.id}>
                  <td className="font-mono text-sm">{t.name}</td>
                  <td className="font-mono text-11 text-muted">{t.slug}</td>
                  <td className="text-11 text-secondary">{t.created_by_username ?? "—"}</td>
                  <td className="text-11 text-muted">{t.member_count}</td>
                  <td className="text-11 text-muted">{t.deployment_count}</td>
                  <td>
                    {t.is_personal && (
                      <span className="personal-badge text-11">Personal</span>
                    )}
                  </td>
                  <td className="font-mono text-11 text-muted">
                    {formatDateTime(t.created_at)}
                  </td>
                  <td>
                    <div className="row-actions">
                      <button
                        className="g-btn g-btn-ghost g-btn-icon row-action-icon"
                        title="Edit team"
                        onClick={() => setEditing(t)}
                      >
                        <Pencil size={ACTION_ICON_SIZE} />
                      </button>
                      {!t.is_personal && (
                        <button
                          className="g-btn g-btn-ghost g-btn-icon row-action-icon"
                          title="Delete team"
                          onClick={() => handleDelete(t)}
                        >
                          <Trash2 size={ACTION_ICON_SIZE} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <TeamEditSheet
        open={!!editing}
        team={editing}
        saveMutation={updateMutation}
        onClose={() => setEditing(null)}
      />
    </div>
  );
}
