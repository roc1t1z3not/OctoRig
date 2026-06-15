"use client";
import "./teams-admin.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { SearchBar } from "@/components/ui/SearchBar";
import { getAdminTeams, type AdminTeam } from "@/lib/api/admin";
import { LoadingCell, EmptyCell } from "@/components/ui/TableStates";
import { formatDateTime } from "@/lib/utils/date";

export default function AdminTeamsPage() {
  const [search, setSearch] = useState("");

  const { data: teams = [], isLoading } = useQuery({
    queryKey: ["admin-teams", search],
    queryFn: () => getAdminTeams({ search: search || undefined }),
  });

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Teams</h1>
        <SearchBar value={search} onChange={setSearch} placeholder="Search teams…" />
      </div>

      <div className="g-panel">
        {isLoading ? (
          <LoadingCell />
        ) : teams.length === 0 ? (
          <EmptyCell label="No teams found." />
        ) : (
          <table className="g-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Slug</th>
                <th>Owner</th>
                <th>Members</th>
                <th>Deployments</th>
                <th>Personal</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {teams.map((t) => (
                <tr key={t.id}>
                  <td className="font-mono text-sm">{t.name}</td>
                  <td className="font-mono text-11 text-muted">{t.slug}</td>
                  <td className="text-11 text-secondary">{t.created_by_username ?? "—"}</td>
                  <td className="text-11 text-muted">{t.member_count}</td>
                  <td className="text-11 text-muted">{t.deployment_count}</td>
                  <td>
                    {t.is_personal && (
                      <span className="personal-badge text-11">Personal</span>
                    )}
                  </td>
                  <td className="font-mono text-11 text-muted">
                    {formatDateTime(t.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
