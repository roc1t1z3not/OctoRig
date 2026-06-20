"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./users-admin.css";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Search, UserPlus, X } from "lucide-react";
import {
  getAdminUsers,
  createAdminUser,
  updateAdminUser,
  resetUserPassword,
  resetUserPoints,
  listRoles,
  type AdminUser,
} from "@/lib/api/admin";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";
import { useUserStore } from "@/stores/user.store";
import { UsersTable } from "@/components/admin/users/UsersTable";
import { CreateUserForm } from "@/components/admin/users/CreateUserForm";
import { useEscapeKey } from "@/hooks/useEscapeKey";

export default function AdminUsersPage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();
  const { user: currentUser } = useUserStore();
  const [showCreate, setShowCreate] = useState(false);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<AdminUser | null>(null);
  const [showReset, setShowReset] = useState(false);
  const [newPw, setNewPw] = useState("");
  const [showRoles, setShowRoles] = useState(false);
  const [pendingRoles, setPendingRoles] = useState<string[]>([]);

  const { data: users = [], isLoading } = useQuery({
    queryKey: ["admin-users", search],
    queryFn: () => getAdminUsers({ search: search || undefined }),
  });

  const { data: availableRoles = [] } = useQuery({
    queryKey: ["admin-roles"],
    queryFn: listRoles,
  });

  const createMutation = useMutation({
    mutationFn: (payload: { username: string; email: string; password: string; platform_roles: string[] }) =>
      createAdminUser(payload),
    onSuccess: (_, { username }) => {
      qc.invalidateQueries({ queryKey: ["admin-users"] });
      push("success", `User ${username} created`);
      setShowCreate(false);
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

  useEscapeKey(() => setShowReset(false), showReset);
  useEscapeKey(() => setShowRoles(false), showRoles);

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
            className="g-btn g-btn-primary g-btn-sm"
            onClick={() => setShowCreate(true)}
          >
            <UserPlus size={13} />
            New User
          </button>
        </div>
      </div>

      <CreateUserForm
        open={showCreate}
        onClose={() => setShowCreate(false)}
        onSubmit={(username, email, password, roles) =>
          createMutation.mutate({ username, email, password, platform_roles: roles })
        }
        isPending={createMutation.isPending}
      />

      <div className="table-wrap g-panel">
        <UsersTable
          users={users}
          isLoading={isLoading}
          onActivate={(u) => {
            if (!u.is_active) {
              updateMutation.mutate({ id: u.id, patch: { is_active: true } });
              return;
            }
            confirm({
              title: `Deactivate ${u.username}?`,
              body: "They will be immediately signed out and unable to log back in until reactivated.",
              confirmLabel: "Deactivate",
              dangerous: true,
              onConfirm: () => updateMutation.mutate({ id: u.id, patch: { is_active: false } }),
            });
          }}
          onManageRoles={(u) => { setSelected(u); setPendingRoles(u.platform_roles); setShowRoles(true); }}
          onResetPassword={(u) => { setSelected(u); setShowReset(true); }}
          onUnlock={(u) => updateMutation.mutate({ id: u.id, patch: { unlock: true } })}
          onResetPoints={(u) => confirm({
            title: `Reset points for ${u.username}?`,
            body: "This will delete all their challenge submissions, scores, and hint unlocks. This cannot be undone.",
            confirmLabel: "Reset Points",
            dangerous: true,
            onConfirm: () => resetPointsMutation.mutate(u.id),
          })}
          isPending={resetPointsMutation.isPending}
          currentUserId={currentUser?.id}
        />
      </div>

      {showReset && selected && (
        <>
          <div className="g-backdrop" onClick={() => setShowReset(false)} />
          <div className="ev-sheet">
            <div className="ev-sheet-header">
              <h2 style={{ margin: 0, fontSize: "1rem", fontWeight: 700 }}>
                Reset Password — {selected.username}
              </h2>
              <button className="g-btn g-btn-ghost g-btn-sm" onClick={() => setShowReset(false)}>
                <X size={14} />
              </button>
            </div>

            <div className="ev-sheet-body">
              <label className="ev-field">
                <span className="ev-label">New Password</span>
                <input
                  className="g-input"
                  type="password"
                  value={newPw}
                  onChange={(e) => setNewPw(e.target.value)}
                  autoFocus
                />
              </label>
            </div>

            <div className="ev-sheet-footer">
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
        </>
      )}

      {showRoles && selected && (
        <>
          <div className="g-backdrop" onClick={() => setShowRoles(false)} />
          <div className="ev-sheet">
            <div className="ev-sheet-header">
              <h2 style={{ margin: 0, fontSize: "1rem", fontWeight: 700 }}>
                Manage Roles — {selected.username}
              </h2>
              <button className="g-btn g-btn-ghost g-btn-sm" onClick={() => setShowRoles(false)}>
                <X size={14} />
              </button>
            </div>

            <div className="ev-sheet-body">
              {availableRoles.map((role) => (
                <label key={role.slug} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={pendingRoles.includes(role.slug)}
                    onChange={() =>
                      setPendingRoles((r) =>
                        r.includes(role.slug) ? r.filter((s) => s !== role.slug) : [...r, role.slug]
                      )
                    }
                  />
                  <span className="text-sm">{role.display_name}</span>
                </label>
              ))}
            </div>

            <div className="ev-sheet-footer">
              <button className="g-btn g-btn-ghost" onClick={() => setShowRoles(false)}>Cancel</button>
              <button
                className="g-btn g-btn-primary"
                disabled={updateMutation.isPending}
                onClick={() => {
                  updateMutation.mutate({ id: selected.id, patch: { platform_roles: pendingRoles } });
                  setShowRoles(false);
                }}
              >
                {updateMutation.isPending ? "Saving…" : "Save Roles"}
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
