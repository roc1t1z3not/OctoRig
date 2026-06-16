"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../deployment-detail.css";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft, CheckCircle2, Clock, ExternalLink,
  RotateCcw, Square, Target,
} from "lucide-react";
import Link from "next/link";
import {
  getDeployment,
  resetDeployment,
  setDeploymentVisibility,
  stopDeployment,
  type Deployment,
} from "@/lib/api/deployments";
import { getLabs, type LabTemplate } from "@/lib/api/labs";
import { getChallenges, type ChallengeDifficulty } from "@/lib/api/challenges";
import { createScheduledAction } from "@/lib/api/scheduler";
import { DeploymentStatusBadge } from "@/components/deployments/DeploymentStatusBadge";
import { DeploymentSidebar } from "@/components/deployments/DeploymentSidebar";
import { ScheduleDestroyModal } from "@/components/deployments/ScheduleDestroyModal";
import { LabCategoryBadge } from "@/components/labs/LabCategoryBadge";
import { LogViewer } from "@/components/deployments/LogViewer";
import { useCountdown } from "@/hooks/useCountdown";
import { useNotificationsStore } from "@/stores/notifications.store";
import { PageSpinner } from "@/components/ui/Spinner";
import { DIFF_COLOR } from "@/lib/utils/difficulty";
import { addHours } from "@/lib/utils/date";

type Visibility = "private" | "team" | "public";

function DiffBadge({ difficulty }: { difficulty: ChallengeDifficulty }) {
  return (
    <span className="dd-diff-badge" style={{ color: DIFF_COLOR[difficulty] }}>{difficulty}</span>
  );
}

export default function DeploymentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const deploymentId = Number(id);
  const qc = useQueryClient();
  const { push } = useNotificationsStore();

  const [showSchedule, setShowSchedule] = useState(false);
  const [scheduledAt, setScheduledAt] = useState(() => addHours(2));

  const { data: deployment, isLoading } = useQuery({
    queryKey: ["deployment", deploymentId],
    queryFn: () => getDeployment(deploymentId),
  });

  const { data: labs = [] } = useQuery<LabTemplate[]>({
    queryKey: ["labs"],
    queryFn: () => getLabs(),
    staleTime: 30_000,
    enabled: !!deployment,
  });

  const lab = deployment ? labs.find((l) => l.slug === deployment.lab_slug) : undefined;

  const { data: challenges = [] } = useQuery({
    queryKey: ["challenges", { lab_slug: deployment?.lab_slug }],
    queryFn: () => getChallenges({ lab_slug: deployment!.lab_slug }),
    enabled: !!deployment?.lab_slug,
  });

  const stopMutation = useMutation({
    mutationFn: () => stopDeployment(deploymentId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["deployment", deploymentId] });
      qc.invalidateQueries({ queryKey: ["deployments"] });
      qc.invalidateQueries({ queryKey: ["labs"] });
      push("success", "Lab stop requested");
    },
    onError: () => push("error", "Failed to stop lab"),
  });

  const resetMutation = useMutation({
    mutationFn: () => resetDeployment(deploymentId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["deployment", deploymentId] });
      push("success", "Lab reset requested");
    },
    onError: () => push("error", "Failed to reset lab"),
  });

  const visMutation = useMutation({
    mutationFn: (v: Visibility) => setDeploymentVisibility(deploymentId, v),
    onSuccess: (updated) => {
      qc.setQueryData(["deployment", deploymentId], updated);
      push("success", `Visibility set to ${updated.visibility}`);
    },
    onError: () => push("error", "Failed to update visibility"),
  });

  const scheduleMutation = useMutation({
    mutationFn: () =>
      createScheduledAction({
        action: "destroy",
        deployment_id: deploymentId,
        scheduled_at: new Date(scheduledAt).toISOString(),
      }),
    onSuccess: () => {
      setShowSchedule(false);
      push("success", "Destroy scheduled");
    },
    onError: (err: any) =>
      push("error", err?.response?.data?.detail ?? "Failed to schedule destroy"),
  });

  const { label: countdown, remainingMs: countdownMs } = useCountdown(deployment?.auto_destroy_at ?? null);

  if (isLoading) return <div className="page"><PageSpinner /></div>;
  if (!deployment) return <div className="page text-muted text-sm">Deployment not found.</div>;

  const isActive = deployment.status === "running" || deployment.status === "starting";
  const canStop = deployment.status === "running" || deployment.status === "error";
  const canReset = deployment.status === "running" && deployment.lab_category === "firerange";
  const canSchedule = deployment.status === "running";
  const vis = (deployment.visibility ?? "private") as Visibility;

  const labUrl = lab?.access_info.find((a) => a.key === "URL")?.value;

  return (
    <div className="page">
      <Link href="/deployments" className="dd-back-link">
        <ArrowLeft size={14} /> Deployments
      </Link>

      <div className="dd-header">
        <div className="dd-title-row">
          <h1 className="dd-title font-mono">{deployment.lab_name}</h1>
          <div className="dd-badges">
            <DeploymentStatusBadge status={deployment.status} />
            <LabCategoryBadge category={deployment.lab_category} />
          </div>
        </div>

        {lab?.description && <p className="dd-desc">{lab.description}</p>}

        <div className="dd-controls">
          {canStop && (
            <button
              className="g-btn g-btn-danger"
              onClick={() => stopMutation.mutate()}
              disabled={stopMutation.isPending || deployment.status === "stopping"}
            >
              <Square size={14} /> Stop
            </button>
          )}
          {canReset && (
            <button
              className="g-btn g-btn-ghost"
              onClick={() => resetMutation.mutate()}
              disabled={resetMutation.isPending}
            >
              <RotateCcw size={14} /> Reset
            </button>
          )}
          {labUrl && isActive && (
            <a href={labUrl} target="_blank" rel="noopener noreferrer" className="g-btn g-btn-ghost">
              <ExternalLink size={14} /> Open Lab
            </a>
          )}
          {canSchedule && (
            <button
              className="g-btn g-btn-ghost g-btn-sm"
              onClick={() => { setShowSchedule(true); setScheduledAt(addHours(2)); }}
            >
              <Clock size={13} /> Schedule Destroy
            </button>
          )}
        </div>
      </div>

      <div className="dd-body">
        <div className="dd-logs g-panel">
          <LogViewer
            deploymentId={deploymentId}
            containerNames={deployment.container_names}
          />
        </div>

        <DeploymentSidebar
          deployment={deployment}
          lab={lab}
          isActive={isActive}
          vis={vis}
          countdown={countdown}
          countdownMs={countdownMs}
          onVisibilityChange={(v) => visMutation.mutate(v)}
          isChangingVisibility={visMutation.isPending}
        />
      </div>

      {challenges.length > 0 && (
        <div className="g-card dd-challenges">
          <div className="dd-section-title">
            Challenges
            <span className="dd-ch-count">{challenges.length}</span>
          </div>
          <div className="dd-ch-list">
            {challenges.map((ch) => (
              <Link key={ch.id} href={`/challenges/${ch.slug}`} className="dd-ch-row">
                <div className="dd-ch-info">
                  <span className="dd-ch-cat">{ch.category.replace("-", " ")}</span>
                  <span className="dd-ch-title">{ch.title}</span>
                  <div className="dd-ch-tags">
                    {ch.tags.slice(0, 4).map((t) => (
                      <span key={t} className="g-tag text-10">{t}</span>
                    ))}
                  </div>
                </div>
                <div className="dd-ch-right">
                  <DiffBadge difficulty={ch.difficulty} />
                  <span className="dd-ch-pts">{ch.points} pts</span>
                  <div className="dd-ch-meta">
                    {ch.estimated_minutes && (
                      <span className="dd-ch-meta-item">
                        <Clock size={10} />{ch.estimated_minutes}m
                      </span>
                    )}
                    <span className="dd-ch-meta-item">
                      <Target size={10} />{ch.solve_count}
                    </span>
                    {ch.solved_by_me && (
                      <span className="dd-ch-solved">
                        <CheckCircle2 size={10} />Solved
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {showSchedule && (
        <ScheduleDestroyModal
          labName={deployment.lab_name}
          scheduledAt={scheduledAt}
          onChangeScheduledAt={setScheduledAt}
          onConfirm={() => scheduleMutation.mutate()}
          onClose={() => setShowSchedule(false)}
          isPending={scheduleMutation.isPending}
        />
      )}
    </div>
  );
}
