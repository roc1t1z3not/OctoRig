"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Play, Square, RotateCcw } from "lucide-react";
import type { LabTemplate } from "@/lib/api/labs";
import { LabCategoryBadge } from "./LabCategoryBadge";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import { StartLabDialog } from "@/components/deployments/StartLabDialog";

interface Props {
  lab: LabTemplate;
  onStop?: (deploymentId: number) => void;
  onReset?: (deploymentId: number) => void;
}

export function LabCard({ lab, onStop, onReset }: Props) {
  const [startOpen, setStartOpen] = useState(false);
  const router = useRouter();
  const deployment = lab.current_deployment;
  const isRunning = deployment?.status === "running" || deployment?.status === "starting";

  const portChips = Object.entries(lab.exposed_ports).map(([name, port]) => (
    <span key={name} className="g-tag text-10">
      {name.toUpperCase()}:{port}
    </span>
  ));

  return (
    <>
      <div
        className="g-card lab-card"
        onClick={() => router.push(`/labs/${lab.slug}`)}
        style={{ cursor: "pointer" }}
      >
        <div className="lab-card-header">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-mono font-bold text-sm">{lab.name}</span>
            <LabCategoryBadge category={lab.category} />
          </div>
          {deployment && <DeploymentStatusBadge status={deployment.status} />}
        </div>

        <p className="text-body text-12 mt-1 mb-2">{lab.description}</p>

        <div className="flex flex-wrap gap-1 mb-3">{portChips}</div>

        <div className="lab-card-actions" onClick={(e) => e.stopPropagation()}>
          {!isRunning ? (
            <button className="g-btn g-btn-primary" onClick={() => setStartOpen(true)}>
              <Play size={14} />
              Start
            </button>
          ) : (
            <>
              <button
                className="g-btn g-btn-danger"
                onClick={() => deployment && onStop?.(deployment.id)}
                disabled={deployment?.status === "stopping"}
              >
                <Square size={14} />
                Stop
              </button>
              {lab.category === "firerange" && (
                <button
                  className="g-btn g-btn-ghost"
                  onClick={() => deployment && onReset?.(deployment.id)}
                  title="Reset scoreboard and restart"
                >
                  <RotateCcw size={14} />
                  Reset
                </button>
              )}
            </>
          )}
        </div>
      </div>

      <StartLabDialog
        lab={lab}
        open={startOpen}
        onClose={() => setStartOpen(false)}
      />

      <style>{`
        .lab-card { padding: 1rem; display: flex; flex-direction: column; }
        .lab-card-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; }
        .lab-card-actions { display: flex; gap: 0.5rem; margin-top: auto; }
      `}</style>
    </>
  );
}
