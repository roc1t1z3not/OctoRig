"use client";
import "./deployments.css";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Square, RotateCcw } from "lucide-react";
import { getDeployments, stopDeployment, resetDeployment } from "@/lib/api/deployments";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import { useNotificationsStore } from "@/stores/notifications.store";

export default function DeploymentsPage() {
  const qc = useQueryClient();
  const router = useRouter();
  const { push } = useNotificationsStore();

  const { data: deployments = [], isLoading } = useQuery({
    queryKey: ["deployments"],
    queryFn: () => getDeployments(),
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

  const resetMutation = useMutation({
    mutationFn: resetDeployment,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["deployments"] });
      qc.invalidateQueries({ queryKey: ["labs"] });
      push("success", "Lab reset requested");
    },
    onError: () => push("error", "Failed to reset lab"),
  });

  return (
    <div className="page">
      <h1 className="page-title font-mono">Deployments</h1>

      {isLoading ? (
        <div className="text-muted text-sm">Loading…</div>
      ) : deployments.length === 0 ? (
        <div className="g-panel empty-state">
          <p className="text-muted text-sm">No deployments yet.</p>
          <Link href="/labs" className="g-btn g-btn-primary mt-2">Start a Lab</Link>
        </div>
      ) : (
        <table className="g-table">
          <thead>
            <tr>
              <th>Lab</th>
              <th>Category</th>
              <th>Status</th>
              <th>Started By</th>
              <th>Started At</th>
              <th>Stopped At</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {deployments.map((d) => {
              const canStop = d.status === "running" || d.status === "starting";
              const canReset = d.status === "running" && d.lab_category === "firerange";
              return (
                <tr
                  key={d.id}
                  className="g-table-row-link"
                  onClick={() => router.push(`/deployments/${d.id}`)}
                >
                  <td className="text-secondary">{d.lab_name}</td>
                  <td className="text-secondary text-11">{d.lab_category}</td>
                  <td><DeploymentStatusBadge status={d.status} /></td>
                  <td className="text-secondary">{d.started_by_username}</td>
                  <td className="font-mono text-11 text-secondary">
                    {d.started_at ? new Date(d.started_at).toLocaleString() : "—"}
                  </td>
                  <td className="font-mono text-11 text-muted">
                    {d.stopped_at ? new Date(d.stopped_at).toLocaleString() : "—"}
                  </td>
                  <td onClick={(e) => e.stopPropagation()}>
                    <div className="flex gap-1">
                      {canStop && (
                        <button
                          className="g-btn g-btn-danger g-btn-icon"
                          onClick={() => stopMutation.mutate(d.id)}
                          disabled={stopMutation.isPending || d.status === "stopping"}
                          title="Stop lab"
                        >
                          <Square size={13} />
                        </button>
                      )}
                      {canReset && (
                        <button
                          className="g-btn g-btn-ghost g-btn-icon"
                          onClick={() => resetMutation.mutate(d.id)}
                          disabled={resetMutation.isPending}
                          title="Reset scoreboard"
                        >
                          <RotateCcw size={13} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
