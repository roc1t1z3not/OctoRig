import { Trash2 } from "lucide-react";
import type { TeamMember, TeamRole } from "@/lib/api/teams";
import { formatDate } from "@/lib/utils/date";

const ALL_ROLES: TeamRole[] = ["owner", "manager", "member", "viewer"];

export function MembersTable({
  members,
  canManage,
  currentUserId,
  onRemove,
  onChangeRole,
  isPending,
}: {
  members: TeamMember[];
  canManage: boolean;
  currentUserId: number;
  onRemove: (userId: number) => void;
  onChangeRole: (userId: number, role: TeamRole) => void;
  isPending: boolean;
}) {
  return (
    <table className="g-table">
      <thead>
        <tr>
          <th>User</th>
          <th>Role</th>
          <th>Joined</th>
          {canManage && <th>Actions</th>}
        </tr>
      </thead>
      <tbody>
        {members.map((m) => {
          const isSelf = m.user_id === currentUserId;
          return (
            <tr key={m.id}>
              <td>
                <span className="font-mono text-sm">{m.username}</span>
                <span className="text-muted text-11 ml-1">{m.email}</span>
              </td>
              <td>
                {canManage && !isSelf ? (
                  <select
                    className="g-select g-select-sm"
                    value={m.role}
                    onChange={(e) => onChangeRole(m.user_id, e.target.value as TeamRole)}
                  >
                    {ALL_ROLES.map((r) => (
                      <option key={r} value={r}>
                        {r.charAt(0).toUpperCase() + r.slice(1)}
                      </option>
                    ))}
                  </select>
                ) : (
                  <span className={`role-badge role-badge--${m.role}`}>{m.role}</span>
                )}
              </td>
              <td className="font-mono text-11 text-muted">{formatDate(m.joined_at)}</td>
              {canManage && (
                <td>
                  {!isSelf && (
                    <button
                      className="g-btn g-btn-danger g-btn-icon"
                      onClick={() => onRemove(m.user_id)}
                      disabled={isPending}
                      title="Remove member"
                    >
                      <Trash2 size={13} />
                    </button>
                  )}
                </td>
              )}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
