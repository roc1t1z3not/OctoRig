"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./users-admin.css";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Search, UserPlus } from "lucide-react";
import {
  getAdminUsers,
  createAdminUser,
  updateAdminUser,
  resetUserPassword,
  resetUserPoints,
  type AdminUser,
} from "@/lib/api/admin";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";
import { UsersTable } from "@/components/admin/users/UsersTable";
import { CreateUserForm } from "@/components/admin/users/CreateUserForm";

type Tab = "list" | "create";

export default function AdminUsersPage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();
  const [tab, setTab] = useState<Tab>("list");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<AdminUser | null>(null);
  const [showReset, setShowReset] = useState(false);
  const [newPw, setNewPw] = useState("");

  const { data: users = [], isLoading } = useQuery({
    queryKey: ["admin-users", search],
    queryFn: () => getAdminUsers({ search: search || undefined }),
  });

  const createMutation = useMutation({
    mutationFn: (payload: { username: string; email: string; password: string; is_admin: boolean }) =>
      createAdminUser(payload),
    onSuccess: (_, { username }) => {
      qc.invalidateQueries({ queryKey: ["admin-users"] });
      push("success", `User ${username} created`);
      setTab("list");
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to create user"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, patch }: { id: number; patch: Parameters<typeof updateAdminUser>[1] }) =>
      updateAdminUser(id, patch),
    onSuccess: (updated) => {
      qc.invalidateQueries({ queryKey: ["admin-users"] });
      setSelected(updated);
      push("success", "User updated");
    },
    onError: () => push("error", "Failed to update user"),
  });

  const resetMutation = useMutation({
    mutationFn: ({ id, password }: { id: number; password: string }) =>
      resetUserPassword(id, password),
    onSuccess: () => {
      setShowReset(false);
      setNewPw("");
      push("success", "Password reset");
    },
    onError: () => push("error", "Failed to reset password"),
  });

  const resetPointsMutation = useMutation({
    mutationFn: (id: number) => resetUserPoints(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-users"] });
      push("success", "Points reset — all submissions and scores cleared");
    },
    onError: () => push("error", "Failed to reset points"),
  });

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Users</h1>
        <div className="header-actions">
          <div className="search-wrap">
            <Search size={13} className="search-icon text-muted" />
            <input
              className="g-input g-input-sm search-input"
              placeholder="Search users…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <button
            className={`g-btn ${tab === "create" ? "g-btn-primary" : "g-btn-ghost"} g-btn-sm`}
            onClick={() => setTab(tab === "create" ? "list" : "create")}
          >
            <UserPlus size={13} />
            {tab === "create" ? "Cancel" : "New User"}
          </button>
        </div>
      </div>

      {tab === "create" && (
        <CreateUserForm
          onSubmit={(username, email, password, is_admin) =>
            createMutation.mutate({ username, email, password, is_admin })
          }
          isPending={createMutation.isPending}
        />
      )}

      <div className="table-wrap g-panel">
        <UsersTable
          users={users}
          isLoading={isLoading}
          onActivate={(u) => updateMutation.mutate({ id: u.id, patch: { is_active: !u.is_active } })}
          onGrantAdmin={(u) => updateMutation.mutate({ id: u.id, patch: { is_admin: !u.is_admin } })}
          onResetPassword={(u) => { setSelected(u); setShowReset(true); }}
          onResetPoints={(u) => confirm({
            title: `Reset points for ${u.username}?`,
            body: "This will delete all their challenge submissions, scores, and hint unlocks. This cannot be undone.",
            confirmLabel: "Reset Points",
            dangerous: true,
            onConfirm: () => resetPointsMutation.mutate(u.id),
          })}
          isPending={resetPointsMutation.isPending}
        />
      </div>

      {showReset && selected && (
        <div className="g-backdrop" onClick={() => setShowReset(false)}>
          <div className="g-modal reset-modal" onClick={(e) => e.stopPropagation()}>
            <div className="g-modal-header">
              <span className="font-mono text-sm">Reset Password — {selected.username}</span>
            </div>
            <div className="g-modal-body">
              <div className="field">
                <label className="text-11 text-muted">New Password</label>
                <input
                  className="g-input"
                  type="password"
                  value={newPw}
                  onChange={(e) => setNewPw(e.target.value)}
                  autoFocus
                />
              </div>
            </div>
            <div className="g-modal-footer">
              <button className="g-btn g-btn-ghost" onClick={() => setShowReset(false)}>Cancel</button>
              <button
                className="g-btn g-btn-primary"
                disabled={!newPw || resetMutation.isPending}
                onClick={() => resetMutation.mutate({ id: selected.id, password: newPw })}
              >
                {resetMutation.isPending ? "Resetting…" : "Reset Password"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
