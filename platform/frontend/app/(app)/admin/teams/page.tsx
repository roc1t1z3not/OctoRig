"use client";
import "./teams-admin.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Search } from "lucide-react";
import { getAdminTeams, type AdminTeam } from "@/lib/api/admin";
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
        <div className="search-wrap">
          <Search size={13} className="search-icon text-muted" />
          <input
            className="g-input g-input-sm search-input"
            placeholder="Search teams…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="g-panel">
        {isLoading ? (
          <div className="loading-cell text-muted text-sm">Loading…</div>
        ) : teams.length === 0 ? (
          <div className="empty-cell text-muted text-sm">No teams found.</div>
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
