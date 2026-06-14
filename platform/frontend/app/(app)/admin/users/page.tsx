"use client";
import "./users-admin.css";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Search, UserPlus, ShieldCheck, ShieldOff, RotateCcw } from "lucide-react";
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

type Tab = "list" | "create";

function RolePill({ label, active }: { label: string; active: boolean }) {
  return (
    <span
      className={`role-pill ${active ? "role-pill--on" : "role-pill--off"}`}
    >
      {label}
    </span>
  );
}

export default function AdminUsersPage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();
  const [tab, setTab] = useState<Tab>("list");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<AdminUser | null>(null);

  // create form
  const [newUsername, setNewUsername] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newIsAdmin, setNewIsAdmin] = useState(false);

  // reset password form
  const [showReset, setShowReset] = useState(false);
  const [newPw, setNewPw] = useState("");

  const { data: users = [], isLoading } = useQuery({
    queryKey: ["admin-users", search],
    queryFn: () => getAdminUsers({ search: search || undefined }),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createAdminUser({
        username: newUsername,
        email: newEmail,
        password: newPassword,
        is_admin: newIsAdmin,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-users"] });
      push("success", `User ${newUsername} created`);
      setTab("list");
      setNewUsername("");
      setNewEmail("");
      setNewPassword("");
      setNewIsAdmin(false);
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
    onSuccess: (_, id) => {
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

      {/* Create form */}
      {tab === "create" && (
        <div className="g-panel create-panel">
          <div className="g-panel-header">
            <span className="font-mono text-sm">New User</span>
          </div>
          <div className="create-body">
            <div className="form-row">
              <div className="field">
                <label className="text-11 text-muted">Username</label>
                <input className="g-input" value={newUsername} onChange={(e) => setNewUsername(e.target.value)} placeholder="username" />
              </div>
              <div className="field">
                <label className="text-11 text-muted">Email</label>
                <input className="g-input" type="email" value={newEmail} onChange={(e) => setNewEmail(e.target.value)} placeholder="user@example.com" />
              </div>
            </div>
            <div className="form-row">
              <div className="field">
                <label className="text-11 text-muted">Password</label>
                <input className="g-input" type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} placeholder="Initial password" />
              </div>
              <div className="field checkbox-field">
                <label className="text-11 text-muted">Admin</label>
                <label className="checkbox-label">
                  <input type="checkbox" checked={newIsAdmin} onChange={(e) => setNewIsAdmin(e.target.checked)} />
                  <span className="text-sm">Grant admin access</span>
                </label>
              </div>
            </div>
            <div className="form-actions">
              <button
                className="g-btn g-btn-primary"
                onClick={() => createMutation.mutate()}
                disabled={!newUsername || !newEmail || !newPassword || createMutation.isPending}
              >
                {createMutation.isPending ? "Creating…" : "Create User"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* User table */}
      <div className="table-wrap g-panel">
        {isLoading ? (
          <div className="loading-cell text-muted text-sm">Loading…</div>
        ) : (
          <table className="g-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Roles</th>
                <th>Teams</th>
                <th>Deployments</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className={!u.is_active ? "row-inactive" : ""}>
                  <td className="font-mono text-sm">{u.username}</td>
                  <td className="text-11 text-muted">{u.email}</td>
                  <td>
                    <div className="role-pills">
                      {u.is_superuser && <RolePill label="Super" active />}
                      {u.is_admin && <RolePill label="Admin" active />}
                      {!u.is_superuser && !u.is_admin && <RolePill label="User" active={false} />}
                    </div>
                  </td>
                  <td className="text-11 text-muted">{u.team_count}</td>
                  <td className="text-11 text-muted">{u.deployment_count}</td>
                  <td>
                    <span className={`status-dot ${u.is_active ? "status-dot--active" : "status-dot--inactive"}`}>
                      {u.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td>
                    <div className="row-actions">
                      <button
                        className="g-btn g-btn-ghost g-btn-icon"
                        title={u.is_active ? "Deactivate" : "Activate"}
                        onClick={() =>
                          updateMutation.mutate({ id: u.id, patch: { is_active: !u.is_active } })
                        }
                      >
                        {u.is_active ? <ShieldOff size={13} /> : <ShieldCheck size={13} />}
                      </button>
                      <button
                        className={`g-btn g-btn-ghost g-btn-icon ${u.is_admin ? "role-on" : ""}`}
                        title={u.is_admin ? "Remove admin" : "Grant admin"}
                        onClick={() =>
                          updateMutation.mutate({ id: u.id, patch: { is_admin: !u.is_admin } })
                        }
                      >
                        <ShieldCheck size={13} />
                      </button>
                      <button
                        className="g-btn g-btn-ghost g-btn-sm"
                        title="Reset password"
                        onClick={() => { setSelected(u); setShowReset(true); }}
                      >
                        Reset PW
                      </button>
                      <button
                        className="g-btn g-btn-ghost g-btn-sm"
                        title="Reset points &amp; submissions"
                        disabled={resetPointsMutation.isPending}
                        onClick={() => confirm({
                          title: `Reset points for ${u.username}?`,
                          body: "This will delete all their challenge submissions, scores, and hint unlocks. This cannot be undone.",
                          confirmLabel: "Reset Points",
                          dangerous: true,
                          onConfirm: () => resetPointsMutation.mutate(u.id),
                        })}
                      >
                        <RotateCcw size={12} />
                        Pts
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Reset password modal */}
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
