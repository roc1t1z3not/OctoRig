// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import Link from "next/link";
import { ShieldCheck, ShieldOff, RotateCcw, UserCog, LockOpen } from "lucide-react";
import type { AdminUser } from "@/lib/api/admin";

function isLocked(u: AdminUser): boolean {
  return !!u.locked_until && new Date(u.locked_until) > new Date();
}

function RolePill({ label }: { label: string }) {
  return <span className="role-pill role-pill--on">{label}</span>;
}

export function UsersTable({
  users,
  isLoading,
  onActivate,
  onManageRoles,
  onResetPassword,
  onResetPoints,
  onUnlock,
  isPending,
}: {
  users: AdminUser[];
  isLoading: boolean;
  onActivate: (user: AdminUser) => void;
  onManageRoles: (user: AdminUser) => void;
  onResetPassword: (user: AdminUser) => void;
  onResetPoints: (user: AdminUser) => void;
  onUnlock: (user: AdminUser) => void;
  isPending: boolean;
}) {
  if (isLoading) {
    return <div className="loading-cell text-muted text-sm">Loading…</div>;
  }

  return (
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
            <td className="font-mono text-sm">
              <Link href={`/profile/${u.username}`} style={{ color: "var(--g-accent)" }}>
                {u.username}
              </Link>
            </td>
            <td className="text-11 text-muted">{u.email}</td>
            <td>
              <div className="role-pills">
                {u.platform_roles.length === 0 && <RolePill label="None" />}
                {u.platform_roles.map((slug) => (
                  <RolePill key={slug} label={slug} />
                ))}
              </div>
            </td>
            <td className="text-11 text-muted">{u.team_count}</td>
            <td className="text-11 text-muted">{u.deployment_count}</td>
            <td>
              <span className={`status-dot ${u.is_active ? "status-dot--active" : "status-dot--inactive"}`}>
                {u.is_active ? "Active" : "Inactive"}
              </span>
              {isLocked(u) && <span className="role-pill role-pill--off" style={{ marginLeft: 6 }}>Locked</span>}
            </td>
            <td>
              <div className="row-actions">
                <button
                  className="g-btn g-btn-ghost g-btn-icon"
                  title={u.is_active ? "Deactivate" : "Activate"}
                  onClick={() => onActivate(u)}
                >
                  {u.is_active ? <ShieldOff size={13} /> : <ShieldCheck size={13} />}
                </button>
                {isLocked(u) && (
                  <button
                    className="g-btn g-btn-ghost g-btn-icon"
                    title="Unlock account"
                    onClick={() => onUnlock(u)}
                  >
                    <LockOpen size={13} />
                  </button>
                )}
                <button
                  className="g-btn g-btn-ghost g-btn-icon"
                  title="Manage roles"
                  onClick={() => onManageRoles(u)}
                >
                  <UserCog size={13} />
                </button>
                <button
                  className="g-btn g-btn-ghost g-btn-sm"
                  title="Reset password"
                  onClick={() => onResetPassword(u)}
                >
                  Reset PW
                </button>
                <button
                  className="g-btn g-btn-ghost g-btn-sm"
                  title="Reset points &amp; submissions"
                  disabled={isPending}
                  onClick={() => onResetPoints(u)}
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
  );
}
