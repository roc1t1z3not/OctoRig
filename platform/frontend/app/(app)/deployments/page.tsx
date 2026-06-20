"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./deployments.css";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Square, RotateCcw, Play, Trash2 } from "lucide-react";
import {
  getDeployments, stopDeployment, resetDeployment, restartDeployment, removeDeployment,
} from "@/lib/api/deployments";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";
import { formatDateTime } from "@/lib/utils/date";

export default function DeploymentsPage() {
  const qc = useQueryClient();
  const router = useRouter();
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();

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

  const startMutation = useMutation({
    mutationFn: restartDeployment,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["deployments"] });
      qc.invalidateQueries({ queryKey: ["labs"] });
      push("success", "Lab start requested");
    },
    onError: () => push("error", "Failed to start lab"),
  });

  const removeMutation = useMutation({
    mutationFn: removeDeployment,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["deployments"] });
      push("success", "Deployment removed");
    },
    onError: () => push("error", "Failed to remove deployment"),
  });

  function handleRemove(id: number, labName: string) {
    confirm({
      title: "Remove deployment?",
      body: `Permanently remove the "${labName}" deployment record? This cannot be undone.`,
      confirmLabel: "Remove",
      dangerous: true,
      onConfirm: () => removeMutation.mutate(id),
    });
  }

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
              const canStart = d.status === "stopped" || d.status === "error";
              const canRemove = d.status === "stopped" || d.status === "error";
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
                    {formatDateTime(d.started_at)}
                  </td>
                  <td className="font-mono text-11 text-muted">
                    {formatDateTime(d.stopped_at)}
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
                      {canStart && (
                        <button
                          className="g-btn g-btn-primary g-btn-icon"
                          onClick={() => startMutation.mutate(d.id)}
                          disabled={startMutation.isPending}
                          title="Start lab"
                        >
                          <Play size={13} />
                        </button>
                      )}
                      {canRemove && (
                        <button
                          className="g-btn g-btn-danger g-btn-icon"
                          onClick={() => handleRemove(d.id, d.lab_name)}
                          disabled={removeMutation.isPending}
                          title="Remove deployment"
                        >
                          <Trash2 size={13} />
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
