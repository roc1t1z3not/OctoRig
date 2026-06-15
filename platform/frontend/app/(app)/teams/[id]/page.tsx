"use client";
import "../teams.css";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, UserPlus } from "lucide-react";
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
import { InviteForm } from "@/components/teams/InviteForm";
import { MembersTable } from "@/components/teams/MembersTable";

export default function TeamDetailPage() {
  const { id } = useParams<{ id: string }>();
  const teamId = Number(id);
  const qc = useQueryClient();
  const { user } = useUserStore();
  const { push } = useNotificationsStore();

  const [showInvite, setShowInvite] = useState(false);

  const { data: team, isLoading: teamLoading } = useQuery({
    queryKey: ["team", teamId],
    queryFn: () => getTeam(teamId),
  });

  const { data: members = [], isLoading: membersLoading } = useQuery({
    queryKey: ["team-members", teamId],
    queryFn: () => getTeamMembers(teamId),
  });

  const inviteMutation = useMutation({
    mutationFn: ({ email, role }: { email: string; role: TeamRole }) =>
      inviteMember(teamId, { email, role }),
    onSuccess: (_, { email }) => {
      push("success", `Invitation sent to ${email}`);
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
          <InviteForm
            onSubmit={(email, role) => inviteMutation.mutate({ email, role })}
            isPending={inviteMutation.isPending}
            onCancel={() => setShowInvite(false)}
          />
        )}

        {membersLoading ? (
          <div className="members-loading text-muted text-11">Loading members…</div>
        ) : (
          <MembersTable
            members={members}
            canManage={!!canManage}
            currentUserId={user?.id ?? -1}
            onRemove={(userId) => removeMutation.mutate(userId)}
            onChangeRole={(userId, role) => roleMutation.mutate({ userId, role })}
            isPending={removeMutation.isPending || roleMutation.isPending}
          />
        )}
      </div>
    </div>
  );
}
