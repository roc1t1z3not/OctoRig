"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./teams.css";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Plus, Users, Crown, Shield, Eye } from "lucide-react";
import { getTeams, type TeamRole } from "@/lib/api/teams";

const ROLE_LABEL: Record<TeamRole, { label: string; icon: React.ReactNode }> = {
  owner:   { label: "Owner",   icon: <Crown   size={11} /> },
  manager: { label: "Manager", icon: <Shield  size={11} /> },
  member:  { label: "Member",  icon: <Users   size={11} /> },
  viewer:  { label: "Viewer",  icon: <Eye     size={11} /> },
};

export default function TeamsPage() {
  const { data: teams = [], isLoading } = useQuery({
    queryKey: ["teams"],
    queryFn: getTeams,
  });

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Teams</h1>
        <Link href="/teams/new" className="g-btn g-btn-primary">
          <Plus size={14} />
          New Team
        </Link>
      </div>

      {isLoading ? (
        <div className="text-muted text-sm">Loading…</div>
      ) : teams.length === 0 ? (
        <div className="g-panel empty-state">
          <Users size={32} className="text-muted" />
          <p className="text-muted text-sm mt-2">No teams yet.</p>
          <Link href="/teams/new" className="g-btn g-btn-primary mt-2">
            Create your first team
          </Link>
        </div>
      ) : (
        <div className="team-grid">
          {teams.map((team) => {
            const role = ROLE_LABEL[team.my_role];
            return (
              <Link key={team.id} href={`/teams/${team.id}`} className="g-card team-card">
                <div className="team-card-header">
                  <span className="team-name font-mono">{team.name}</span>
                  <span className={`role-badge role-badge--${team.my_role}`}>
                    {role.icon}
                    {role.label}
                  </span>
                </div>
                {team.description && (
                  <p className="text-muted text-11 team-desc">{team.description}</p>
                )}
                <div className="team-meta">
                  <span className="text-muted text-11">
                    <Users size={11} /> {team.member_count} member{team.member_count !== 1 ? "s" : ""}
                  </span>
                  {team.is_personal && (
                    <span className="personal-badge text-11">Personal</span>
                  )}
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
