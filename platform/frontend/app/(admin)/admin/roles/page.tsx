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
import { RoleFormSheet } from "@/components/admin/roles/RoleFormSheet";

export default function AdminRolesPage() {
  useAdminGuard();
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();

  const [sheetOpen, setSheetOpen] = useState(false);
  const [selected, setSelected] = useState<PlatformRole | null>(null);

  const { data: roles = [], isLoading } = useQuery({
    queryKey: ["admin-roles"],
    queryFn: listRoles,
  });

  function openCreate() {
    setSelected(null);
    setSheetOpen(true);
  }

  function openEdit(role: PlatformRole) {
    setSelected(role);
    setSheetOpen(true);
  }

  function closeSheet() {
    setSheetOpen(false);
    setSelected(null);
  }

  const saveMutation = useMutation({
    mutationFn: (payload: any) =>
      selected ? updateRole(selected.slug, payload) : createRole(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-roles"] });
      push("success", selected ? "Role updated." : "Role created.");
      closeSheet();
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to save role."),
  });

  const deleteMutation = useMutation({
    mutationFn: (slug: string) => deleteRole(slug),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-roles"] });
      push("success", "Role deleted.");
      closeSheet();
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to delete role."),
  });

  const toggleDefaultMutation = useMutation({
    mutationFn: ({ slug, is_default }: { slug: string; is_default: boolean }) =>
      updateRole(slug, { is_default }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-roles"] });
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to update role."),
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
                <th>Default</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {roles.map((role) => {
                const isAdmin = role.slug === "admin";
                return (
                  <tr
                    key={role.slug}
                    onClick={() => !isAdmin && openEdit(role)}
                    style={{ cursor: isAdmin ? "default" : "pointer" }}
                  >
                    <td className="font-mono text-sm">{role.slug}</td>
                    <td className="text-sm">{role.display_name}</td>
                    <td className="text-11 text-muted">{role.permissions.length}</td>
                    <td>
                      <span className={`role-pill ${role.is_system ? "role-pill--on" : "role-pill--off"}`}>
                        {role.is_system ? "System" : "Custom"}
                      </span>
                    </td>
                    <td>
                      <label
                        className="toggle"
                        title={isAdmin ? "The admin role cannot be edited" : "Assign automatically to new users"}
                        onClick={(e) => e.stopPropagation()}
                      >
                        <input
                          type="checkbox"
                          checked={role.is_default}
                          disabled={isAdmin || toggleDefaultMutation.isPending}
                          onChange={(e) =>
                            toggleDefaultMutation.mutate({ slug: role.slug, is_default: e.target.checked })
                          }
                        />
                        <span className="toggle-track" />
                      </label>
                    </td>
                    <td>
                      {!role.is_system && (
                        <button
                          className="g-btn g-btn-ghost g-btn-icon"
                          title="Delete role"
                          onClick={(e) => { e.stopPropagation(); handleDelete(role); }}
                        >
                          <Trash2 size={13} />
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      <RoleFormSheet
        open={sheetOpen}
        initialValues={selected}
        saveMutation={saveMutation}
        onClose={closeSheet}
      />
    </div>
  );
}
