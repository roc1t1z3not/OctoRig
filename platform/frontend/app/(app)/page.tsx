"use client";
import "./dashboard.css";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { ExternalLink } from "lucide-react";
import { getDeployments, stopDeployment } from "@/lib/api/deployments";
import { getHealth, getContainers } from "@/lib/api/system";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import { useNotificationsStore } from "@/stores/notifications.store";

export default function Dashboard() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();

  const { data: deployments = [], isLoading } = useQuery({
    queryKey: ["deployments"],
    queryFn: () => getDeployments(),
  });
  const { data: containers = [] } = useQuery({
    queryKey: ["containers"],
    queryFn: getContainers,
  });
  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: getHealth,
    refetchInterval: 30_000,
  });

  const stopMutation = useMutation({
    mutationFn: stopDeployment,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["deployments"] });
      qc.invalidateQueries({ queryKey: ["labs"] });
      push("success", "Lab stop requested");
    },
    onError: () => push("error", "Failed to stop lab"),
  });

  const activeDeployments = deployments.filter((d) => d.status !== "stopped");
  const knownNames = new Set(deployments.flatMap((d) => d.container_names));
  const externalContainers = containers.filter(
    (c) => !knownNames.has(c.name) && c.name.startsWith("octorig-") && !c.name.includes("platform")
  );

  return (
    <div className="page">
      <h1 className="page-title font-mono">Dashboard</h1>

      {/* Stat cards */}
      <div className="stat-row">
        <div className="g-card stat-card">
          <span className="text-muted text-11">Running Labs</span>
          <span className="stat-value text-accent">{health?.running_labs ?? "—"}</span>
        </div>
        <div className="g-card stat-card">
          <span className="text-muted text-11">Total Containers</span>
          <span className="stat-value">{health?.total_containers ?? "—"}</span>
        </div>
        <div className="g-card stat-card">
          <span className="text-muted text-11">Docker</span>
          <span className={`stat-value ${health?.docker === "ok" ? "text-success" : "text-danger"}`}>
            {health?.docker === "ok" ? "Healthy" : "-"}
          </span>
        </div>
      </div>

      {/* Active deployments */}
      <section className="mt-4">
        <h2 className="section-title font-mono">Active Deployments</h2>
        {isLoading ? (
          <div className="text-muted text-sm">Loading…</div>
        ) : activeDeployments.length === 0 ? (
          <div className="g-panel empty-state">
            <p className="text-muted text-sm">No active labs.</p>
            <Link href="/labs" className="g-btn g-btn-primary mt-2">Browse Lab Catalog</Link>
          </div>
        ) : (
          <table className="g-table">
            <thead>
              <tr>
                <th>Lab</th>
                <th>Status</th>
                <th>Started By</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {activeDeployments.map((d) => (
                <tr key={d.id}>
                  <td>
                    <Link href={`/deployments/${d.id}`} className="text-accent flex items-center gap-1">
                      {d.lab_name}
                      <ExternalLink size={12} />
                    </Link>
                  </td>
                  <td><DeploymentStatusBadge status={d.status} /></td>
                  <td className="text-secondary">{d.started_by_username}</td>
                  <td>
                    <button
                      className="g-btn g-btn-danger g-btn-icon"
                      onClick={() => stopMutation.mutate(d.id)}
                      disabled={d.status === "stopping" || stopMutation.isPending}
                      title="Stop lab"
                    >
                      ■
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {/* Externally managed (CLI-started) */}
      {externalContainers.length > 0 && (
        <section className="mt-4">
          <h2 className="section-title font-mono">
            Externally Managed
            <span className="g-badge ml-2" style={{ color: "var(--g-warning)" }}>CLI</span>
          </h2>
          <div className="g-panel">
            <p className="text-muted text-11 mb-2">Containers started via the CLI — read-only in this view.</p>
            <table className="g-table">
              <thead><tr><th>Container</th><th>Status</th><th>Image</th></tr></thead>
              <tbody>
                {externalContainers.map((c) => (
                  <tr key={c.name}>
                    <td className="font-mono text-11">{c.name}</td>
                    <td><DeploymentStatusBadge status={c.status === "running" ? "running" : "stopped"} /></td>
                    <td className="text-secondary text-11">{c.image}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
