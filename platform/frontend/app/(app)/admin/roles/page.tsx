"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./roles-admin.css";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2 } from "lucide-react";
import {
  listRoles,
  createRole,
  updateRole,
  deleteRole,
  type PlatformRole,
} from "@/lib/api/admin";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";
import { useAdminGuard } from "@/hooks/useAdminGuard";

const PERMISSION_GROUPS = [
  {
    label: "Platform Pages",
    perms: [
      { key: "platform.dashboard", label: "Dashboard" },
      { key: "platform.challenges", label: "Challenges" },
      { key: "platform.events", label: "Events" },
      { key: "platform.scoreboard", label: "Scoreboard" },
      { key: "platform.badges", label: "Badges" },
      { key: "platform.labs", label: "Labs" },
      { key: "platform.deployments", label: "Deployments" },
      { key: "platform.teams", label: "Teams" },
    ],
  },
  {
    label: "Admin Section",
    perms: [
      { key: "admin.panel", label: "Admin Panel Access" },
      { key: "admin.users.view", label: "View Users" },
      { key: "admin.users.manage", label: "Manage Users" },
      { key: "admin.teams.view", label: "View Teams" },
      { key: "admin.deployments.view", label: "View Deployments" },
      { key: "admin.deployments.manage", label: "Manage Deployments" },
      { key: "admin.audit.view", label: "View Audit Log" },
      { key: "admin.challenges.manage", label: "Manage Challenges" },
      { key: "admin.events.manage", label: "Manage Events" },
      { key: "admin.api_keys.view", label: "View API Keys" },
      { key: "admin.ranks.manage", label: "Manage Ranks" },
      { key: "admin.assessments.manage", label: "Manage Assessments" },
      { key: "admin.content.manage", label: "Content Moderation" },
      { key: "admin.settings.manage", label: "Platform Settings" },
    ],
  },
  {
    label: "Creator",
    perms: [{ key: "creator.access", label: "Creator Access" }],
  },
];

const EMPTY_FORM = { slug: "", display_name: "", description: "", permissions: [] as string[], is_default: false };

export default function AdminRolesPage() {
  useAdminGuard();
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();

  const [selected, setSelected] = useState<PlatformRole | null>(null);
  const [form, setForm] = useState(EMPTY_FORM);

  const { data: roles = [], isLoading } = useQuery({
    queryKey: ["admin-roles"],
    queryFn: listRoles,
  });

  function openCreate() {
    setSelected(null);
    setForm(EMPTY_FORM);
  }

  function openEdit(role: PlatformRole) {
    setSelected(role);
    setForm({
      slug: role.slug,
      display_name: role.display_name,
      description: role.description ?? "",
      permissions: role.permissions,
      is_default: role.is_default,
    });
  }

  function closePanel() {
    setSelected(null);
    setForm(EMPTY_FORM);
  }

  function togglePerm(key: string) {
    setForm((f) => ({
      ...f,
      permissions: f.permissions.includes(key)
        ? f.permissions.filter((p) => p !== key)
        : [...f.permissions, key],
    }));
  }

  const saveMutation = useMutation({
    mutationFn: () =>
      selected
        ? updateRole(selected.slug, {
            display_name: form.display_name,
            description: form.description || undefined,
            permissions: form.permissions,
            is_default: form.is_default,
          })
        : createRole({
            slug: form.slug,
            display_name: form.display_name,
            description: form.description || undefined,
            permissions: form.permissions,
            is_default: form.is_default,
          }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-roles"] });
      push("success", selected ? "Role updated." : "Role created.");
      closePanel();
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to save role."),
  });

  const deleteMutation = useMutation({
    mutationFn: (slug: string) => deleteRole(slug),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-roles"] });
      push("success", "Role deleted.");
      closePanel();
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to delete role."),
  });

  function handleDelete(role: PlatformRole) {
    confirm({
      title: "Delete role",
      body: `Delete "${role.display_name}"? Users holding this role will lose its permissions.`,
      confirmLabel: "Delete",
      dangerous: true,
      onConfirm: () => deleteMutation.mutate(role.slug),
    });
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title font-mono">Roles</h1>
          <p className="page-sub">{roles.length} roles configured</p>
        </div>
        <button className="g-btn g-btn-primary" onClick={openCreate}>
          <Plus size={13} />
          New Role
        </button>
      </div>

      <div className="roles-grid">
        <div className="g-card" style={{ padding: 0, overflow: "hidden" }}>
          {isLoading ? (
            <div className="loading-cell text-muted text-sm">Loading…</div>
          ) : (
            <table className="g-table">
              <thead>
                <tr>
                  <th>Slug</th>
                  <th>Name</th>
                  <th>Permissions</th>
                  <th>Type</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {roles.map((role) => (
                  <tr key={role.slug} onClick={() => openEdit(role)} style={{ cursor: "pointer" }}>
                    <td className="font-mono text-sm">{role.slug}</td>
                    <td className="text-sm">{role.display_name}</td>
                    <td className="text-11 text-muted">{role.permissions.length}</td>
                    <td>
                      <span className={`role-pill ${role.is_system ? "role-pill--on" : "role-pill--off"}`}>
                        {role.is_system ? "System" : "Custom"}
                      </span>
                    </td>
                    <td>
                      <button
                        className="g-btn g-btn-ghost g-btn-icon"
                        title={role.is_system ? "System roles cannot be deleted" : "Delete role"}
                        disabled={role.is_system}
                        onClick={(e) => { e.stopPropagation(); handleDelete(role); }}
                      >
                        <Trash2 size={13} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="g-panel">
          <div className="g-panel-header">
            <span className="font-mono text-sm">{selected ? `Edit — ${selected.slug}` : "New Role"}</span>
          </div>
          <div className="create-body">
            {!selected && (
              <div className="field">
                <label className="text-11 text-muted">Slug</label>
                <input
                  className="g-input"
                  value={form.slug}
                  onChange={(e) => setForm((f) => ({ ...f, slug: e.target.value }))}
                  placeholder="custom-role"
                />
              </div>
            )}
            <div className="field">
              <label className="text-11 text-muted">Display Name</label>
              <input
                className="g-input"
                value={form.display_name}
                onChange={(e) => setForm((f) => ({ ...f, display_name: e.target.value }))}
                placeholder="Custom Role"
              />
            </div>
            <div className="field">
              <label className="text-11 text-muted">Description</label>
              <input
                className="g-input"
                value={form.description}
                onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                placeholder="What this role grants"
              />
            </div>
            <div className="field checkbox-field">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={form.is_default}
                  onChange={(e) => setForm((f) => ({ ...f, is_default: e.target.checked }))}
                />
                <span className="text-sm">Assign automatically to new users</span>
              </label>
            </div>

            {PERMISSION_GROUPS.map((group) => (
              <div className="perm-group" key={group.label}>
                <div className="perm-group-title">{group.label}</div>
                {group.perms.map((perm) => (
                  <label key={perm.key} className="perm-checkbox">
                    <input
                      type="checkbox"
                      checked={form.permissions.includes(perm.key)}
                      onChange={() => togglePerm(perm.key)}
                    />
                    {perm.label}
                  </label>
                ))}
              </div>
            ))}

            <div className="form-actions">
              {selected && (
                <button className="g-btn g-btn-ghost" onClick={closePanel}>Cancel</button>
              )}
              <button
                className="g-btn g-btn-primary"
                disabled={!form.display_name || (!selected && !form.slug) || saveMutation.isPending}
                onClick={() => saveMutation.mutate()}
              >
                {saveMutation.isPending ? "Saving…" : selected ? "Save Changes" : "Create Role"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
