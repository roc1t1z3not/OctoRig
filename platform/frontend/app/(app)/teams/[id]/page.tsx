"use client";
import "../teams.css";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, UserPlus, Trash2, Crown, MoreHorizontal } from "lucide-react";
import Link from "next/link";
import {
  getTeam,
  getTeamMembers,
  inviteMember,
  removeMember,
  changeMemberRole,
  type TeamRole,
} from "@/lib/api/teams";
import { useUserStore } from "@/stores/user.store";
import { useNotificationsStore } from "@/stores/notifications.store";

const ROLE_ORDER: TeamRole[] = ["owner", "manager", "member", "viewer"];

export default function TeamDetailPage() {
  const { id } = useParams<{ id: string }>();
  const teamId = Number(id);
  const router = useRouter();
  const qc = useQueryClient();
  const { user } = useUserStore();
  const { push } = useNotificationsStore();

  const [showInvite, setShowInvite] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState<TeamRole>("member");

  const { data: team, isLoading: teamLoading } = useQuery({
    queryKey: ["team", teamId],
    queryFn: () => getTeam(teamId),
  });

  const { data: members = [], isLoading: membersLoading } = useQuery({
    queryKey: ["team-members", teamId],
    queryFn: () => getTeamMembers(teamId),
  });

  const inviteMutation = useMutation({
    mutationFn: () => inviteMember(teamId, { email: inviteEmail, role: inviteRole }),
    onSuccess: () => {
      push("success", `Invitation sent to ${inviteEmail}`);
      setInviteEmail("");
      setShowInvite(false);
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to send invitation"),
  });

  const removeMutation = useMutation({
    mutationFn: (userId: number) => removeMember(teamId, userId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["team-members", teamId] });
      push("success", "Member removed");
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to remove member"),
  });

  const roleMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: number; role: TeamRole }) =>
      changeMemberRole(teamId, userId, role),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["team-members", teamId] });
      push("success", "Role updated");
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to update role"),
  });

  const canManage =
    team?.my_role === "owner" || team?.my_role === "manager" ||
    user?.is_admin || user?.is_superuser;

  if (teamLoading) return <div className="page text-muted text-sm">Loading…</div>;
  if (!team) return <div className="page text-muted text-sm">Team not found.</div>;

  return (
    <div className="page">
      <div className="page-header">
        <Link href="/teams" className="back-link text-muted text-sm">
          <ArrowLeft size={14} />
          Teams
        </Link>
      </div>

      <div className="team-header g-panel">
        <div className="g-panel-header">
          <div>
            <h1 className="font-mono" style={{ fontSize: "1rem" }}>{team.name}</h1>
            {team.description && (
              <p className="text-muted text-11 mt-1">{team.description}</p>
            )}
          </div>
          <span className={`role-badge role-badge--${team.my_role}`}>{team.my_role}</span>
        </div>
      </div>

      <div className="members-panel g-panel mt-3">
        <div className="g-panel-header">
          <span className="font-mono text-sm">Members ({members.length})</span>
          {canManage && (
            <button
              className="g-btn g-btn-ghost g-btn-sm"
              onClick={() => setShowInvite(!showInvite)}
            >
              <UserPlus size={13} />
              Invite
            </button>
          )}
        </div>

        {showInvite && (
          <div className="invite-form">
            <input
              className="g-input g-input-sm"
              placeholder="email@example.com"
              type="email"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              autoFocus
            />
            <select
              className="g-select g-select-sm"
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value as TeamRole)}
            >
              {ROLE_ORDER.filter(r => r !== "owner").map(r => (
                <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
              ))}
            </select>
            <button
              className="g-btn g-btn-primary g-btn-sm"
              onClick={() => inviteMutation.mutate()}
              disabled={!inviteEmail || inviteMutation.isPending}
            >
              {inviteMutation.isPending ? "Sending…" : "Send"}
            </button>
            <button
              className="g-btn g-btn-ghost g-btn-sm"
              onClick={() => setShowInvite(false)}
            >
              Cancel
            </button>
          </div>
        )}

        {membersLoading ? (
          <div className="members-loading text-muted text-11">Loading members…</div>
        ) : (
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
                const isSelf = m.user_id === user?.id;
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
                          onChange={(e) =>
                            roleMutation.mutate({ userId: m.user_id, role: e.target.value as TeamRole })
                          }
                        >
                          {ROLE_ORDER.map(r => (
                            <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
                          ))}
                        </select>
                      ) : (
                        <span className={`role-badge role-badge--${m.role}`}>{m.role}</span>
                      )}
                    </td>
                    <td className="font-mono text-11 text-muted">
                      {new Date(m.joined_at).toLocaleDateString()}
                    </td>
                    {canManage && (
                      <td>
                        {!isSelf && (
                          <button
                            className="g-btn g-btn-danger g-btn-icon"
                            onClick={() => removeMutation.mutate(m.user_id)}
                            disabled={removeMutation.isPending}
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
        )}
      </div>
    </div>
  );
}
