"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./admin-deployments.css";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { Trash2, RefreshCw, StopCircle, Play, X } from "lucide-react";
import { SearchBar } from "@/components/ui/SearchBar";
import { getAdminDeployments, stopAllDeployments, type AdminDeployment } from "@/lib/api/admin";
import { stopDeployment, resetDeployment, restartDeployment, removeDeployment } from "@/lib/api/deployments";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import { LoadingCell, EmptyCell } from "@/components/ui/TableStates";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";
import { formatDateTime } from "@/lib/utils/date";

const ACTIVE_STATUSES = new Set(["starting", "running", "error"]);
const STOPPABLE_STATUSES = new Set(["stopped", "error"]);

export default function AdminDeploymentsPage() {
  const [search, setSearch] = useState("");
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();
  const qc = useQueryClient();
  const router = useRouter();

  const { data: deployments = [], isLoading } = useQuery<AdminDeployment[]>({
    queryKey: ["admin-deployments", search],
    queryFn: () => getAdminDeployments({ search: search || undefined }),
  });

  const destroyMutation = useMutation({
    mutationFn: stopDeployment,
    onSuccess: () => {
      push("success", "Deployment stopped");
      qc.invalidateQueries({ queryKey: ["admin-deployments"] });
    },
    onError: () => push("error", "Failed to stop deployment"),
  });

  const resetMutation = useMutation({
    mutationFn: resetDeployment,
    onSuccess: () => {
      push("success", "Deployment reset");
      qc.invalidateQueries({ queryKey: ["admin-deployments"] });
    },
    onError: () => push("error", "Failed to reset deployment"),
  });

  function handleDestroy(d: AdminDeployment) {
    confirm({
      title: "Destroy deployment?",
      body: `Stop and destroy the "${d.lab_name}" lab for ${d.started_by_username}? The container will be removed.`,
      confirmLabel: "Destroy",
      dangerous: true,
      onConfirm: () => destroyMutation.mutate(d.id),
    });
  }

  function handleReset(d: AdminDeployment) {
    confirm({
      title: "Reset deployment?",
      body: `Reset the "${d.lab_name}" lab for ${d.started_by_username}? The container will restart with a fresh state.`,
      confirmLabel: "Reset",
      onConfirm: () => resetMutation.mutate(d.id),
    });
  }

  const startMutation = useMutation({
    mutationFn: restartDeployment,
    onSuccess: () => {
      push("success", "Deployment start requested");
      qc.invalidateQueries({ queryKey: ["admin-deployments"] });
    },
    onError: () => push("error", "Failed to start deployment"),
  });

  const removeMutation = useMutation({
    mutationFn: removeDeployment,
    onSuccess: () => {
      push("success", "Deployment removed");
      qc.invalidateQueries({ queryKey: ["admin-deployments"] });
    },
    onError: () => push("error", "Failed to remove deployment"),
  });

  function handleRemove(d: AdminDeployment) {
    confirm({
      title: "Remove deployment?",
      body: `Permanently remove the "${d.lab_name}" deployment record for ${d.started_by_username}? This cannot be undone.`,
      confirmLabel: "Remove",
      dangerous: true,
      onConfirm: () => removeMutation.mutate(d.id),
    });
  }

  const stopAllMutation = useMutation({
    mutationFn: stopAllDeployments,
    onSuccess: () => {
      push("success", "All labs are being stopped");
      qc.invalidateQueries({ queryKey: ["admin-deployments"] });
    },
    onError: () => push("error", "Failed to stop all deployments"),
  });

  function handleStopAll() {
    const activeCount = deployments.filter((d) => ACTIVE_STATUSES.has(d.status)).length;
    confirm({
      title: "Stop all labs?",
      body: `This will stop all ${activeCount} running or starting deployment${activeCount !== 1 ? "s" : ""} across every user. This cannot be undone.`,
      confirmLabel: "Stop All",
      dangerous: true,
      onConfirm: () => stopAllMutation.mutate(),
    });
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">All Deployments</h1>
        <SearchBar value={search} onChange={setSearch} placeholder="Filter by user or lab…" />
        {deployments.some((d) => ACTIVE_STATUSES.has(d.status)) && (
          <button
            className="g-btn g-btn-danger g-btn-sm"
            disabled={stopAllMutation.isPending}
            onClick={handleStopAll}
          >
            <StopCircle size={14} />
            {stopAllMutation.isPending ? "Stopping…" : "Stop All"}
          </button>
        )}
      </div>

      <div className="g-panel">
        {isLoading ? (
          <LoadingCell />
        ) : deployments.length === 0 ? (
          <EmptyCell label="No deployments." />
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
                <th></th>
              </tr>
            </thead>
            <tbody>
              {deployments.map((d) => {
                const isActive = ACTIVE_STATUSES.has(d.status);
                const isStoppable = STOPPABLE_STATUSES.has(d.status);
                return (
                  <tr
                    key={d.id}
                    className="g-table-row-link"
                    onClick={() => router.push(`/deployments/${d.id}`)}
                  >
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
                      {formatDateTime(d.started_at)}
                    </td>
                    <td className="font-mono text-11 text-muted">
                      {formatDateTime(d.stopped_at)}
                    </td>
                    <td onClick={(e) => e.stopPropagation()}>
                      <div style={{ display: "flex", gap: 4 }}>
                        {isActive && (
                          <>
                            <button
                              className="g-btn g-btn-ghost g-btn-sm"
                              title="Reset"
                              disabled={resetMutation.isPending}
                              onClick={() => handleReset(d)}
                            >
                              <RefreshCw size={12} />
                            </button>
                            <button
                              className="g-btn g-btn-danger g-btn-sm"
                              title="Destroy"
                              disabled={destroyMutation.isPending}
                              onClick={() => handleDestroy(d)}
                            >
                              <Trash2 size={12} />
                            </button>
                          </>
                        )}
                        {isStoppable && (
                          <>
                            <button
                              className="g-btn g-btn-primary g-btn-sm"
                              title="Start"
                              disabled={startMutation.isPending}
                              onClick={() => startMutation.mutate(d.id)}
                            >
                              <Play size={12} />
                            </button>
                            <button
                              className="g-btn g-btn-danger g-btn-sm"
                              title="Remove"
                              disabled={removeMutation.isPending}
                              onClick={() => handleRemove(d)}
                            >
                              <X size={12} />
                            </button>
                          </>
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
    </div>
  );
}
