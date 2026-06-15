import Link from "next/link";
import { ShieldCheck, ShieldOff, RotateCcw } from "lucide-react";
import type { AdminUser } from "@/lib/api/admin";

function RolePill({ label, active }: { label: string; active: boolean }) {
  return (
    <span className={`role-pill ${active ? "role-pill--on" : "role-pill--off"}`}>
      {label}
    </span>
  );
}

export function UsersTable({
  users,
  isLoading,
  onActivate,
  onGrantAdmin,
  onResetPassword,
  onResetPoints,
  isPending,
}: {
  users: AdminUser[];
  isLoading: boolean;
  onActivate: (user: AdminUser) => void;
  onGrantAdmin: (user: AdminUser) => void;
  onResetPassword: (user: AdminUser) => void;
  onResetPoints: (user: AdminUser) => void;
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
                  onClick={() => onActivate(u)}
                >
                  {u.is_active ? <ShieldOff size={13} /> : <ShieldCheck size={13} />}
                </button>
                <button
                  className={`g-btn g-btn-ghost g-btn-icon ${u.is_admin ? "role-on" : ""}`}
                  title={u.is_admin ? "Remove admin" : "Grant admin"}
                  onClick={() => onGrantAdmin(u)}
                >
                  <ShieldCheck size={13} />
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
