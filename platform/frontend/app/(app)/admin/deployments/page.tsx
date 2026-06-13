"use client";
import "./admin-deployments.css";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { getAdminDeployments, type AdminDeployment } from "@/lib/api/admin";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";

export default function AdminDeploymentsPage() {
  const [search, setSearch] = useState("");

  const { data: deployments = [], isLoading } = useQuery<AdminDeployment[]>({
    queryKey: ["admin-deployments", search],
    queryFn: () => getAdminDeployments({ search: search || undefined }),
  });

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">All Deployments</h1>
        <div className="search-wrap">
          <Search size={13} className="search-icon text-muted" />
          <input
            className="g-input g-input-sm search-input"
            placeholder="Filter by user or lab…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="g-panel">
        {isLoading ? (
          <div className="loading-cell text-muted text-sm">Loading…</div>
        ) : deployments.length === 0 ? (
          <div className="empty-cell text-muted text-sm">No deployments.</div>
        ) : (
          <table className="g-table">
            <thead>
              <tr>
                <th>Lab</th>
                <th>User</th>
                <th>Team</th>
                <th>Visibility</th>
                <th>Status</th>
                <th>Started</th>
                <th>Stopped</th>
              </tr>
            </thead>
            <tbody>
              {deployments.map((d) => (
                <tr key={d.id}>
                  <td className="font-mono text-sm">{d.lab_name}</td>
                  <td className="text-11 text-secondary">{d.started_by_username}</td>
                  <td className="text-11 text-muted">{d.team_name ?? "—"}</td>
                  <td>
                    <span className={`vis-badge vis-badge--${d.visibility ?? "private"}`}>
                      {d.visibility ?? "private"}
                    </span>
                  </td>
                  <td>
                    <DeploymentStatusBadge status={d.status} />
                  </td>
                  <td className="font-mono text-11 text-muted">
                    {d.started_at ? new Date(d.started_at).toLocaleString() : "—"}
                  </td>
                  <td className="font-mono text-11 text-muted">
                    {d.stopped_at ? new Date(d.stopped_at).toLocaleString() : "—"}
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
