"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../admin.css";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { Plus, ClipboardList, Users } from "lucide-react";
import { listAssessments, createAssessment, type Assessment } from "@/lib/api/assessments";
import { getLabs, type LabTemplate } from "@/lib/api/labs";
import { useUserStore } from "@/stores/user.store";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useNotificationsStore } from "@/stores/notifications.store";
import { AssessmentFormSheet } from "@/components/admin/assessments/AssessmentFormSheet";

function StatusBadge({ isActive }: { isActive: boolean }) {
  return (
    <span className={`role-pill ${isActive ? "role-pill--on" : "role-pill--off"}`}>
      {isActive ? "active" : "inactive"}
    </span>
  );
}

export default function AdminAssessmentsPage() {
  const { user } = useUserStore();
  const router = useRouter();
  const { push } = useNotificationsStore();
  const qc = useQueryClient();
  const [sheetOpen, setSheetOpen] = useState(false);

  useEffect(() => {
    if (user && !user.is_admin && !user.is_superuser) router.replace("/");
  }, [user, router]);

  const { data: assessments = [], isLoading } = useQuery({
    queryKey: ["admin-assessments"],
    queryFn: listAssessments,
    enabled: !!(user?.is_admin || user?.is_superuser),
  });

  const { data: labs = [], isLoading: labsLoading } = useQuery<LabTemplate[]>({
    queryKey: ["labs", "world"],
    queryFn: () => getLabs("world"),
    staleTime: 60_000,
  });

  const createMutation = useMutation({
    mutationFn: createAssessment,
    onSuccess: (assessment) => {
      qc.invalidateQueries({ queryKey: ["admin-assessments"] });
      push("success", `Assessment "${assessment.name}" created`);
      setSheetOpen(false);
      router.push(`/admin/assessments/${assessment.id}`);
    },
    onError: (err: any) =>
      push("error", err?.response?.data?.detail ?? "Failed to create assessment"),
  });

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Assessments</h1>
        <button
          className="g-btn g-btn-primary g-btn-sm"
          onClick={() => setSheetOpen(true)}
        >
          <Plus size={14} />
          New Assessment
        </button>
      </div>

      {isLoading ? (
        <p className="text-muted text-sm">Loading…</p>
      ) : assessments.length === 0 ? (
        <div className="empty-state">
          <ClipboardList size={40} strokeWidth={1.2} />
          <p>No assessments yet.</p>
          <button
            className="g-btn g-btn-primary g-btn-sm"
            onClick={() => setSheetOpen(true)}
          >
            Create your first assessment
          </button>
        </div>
      ) : (
        <table className="g-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Company</th>
              <th>Labs</th>
              <th>Duration</th>
              <th>Candidates</th>
              <th>Active</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {assessments.map((a: Assessment) => (
              <tr key={a.id}>
                <td style={{ fontWeight: 500, color: "var(--g-text)" }}>{a.name}</td>
                <td style={{ color: "var(--g-text-muted)", fontSize: "0.8rem" }}>
                  {a.company_name ?? <span style={{ opacity: 0.4 }}>—</span>}
                </td>
                <td style={{ fontFamily: "var(--font-mono, monospace)", fontSize: "0.75rem" }}>
                  {a.lab_slugs.length}
                </td>
                <td style={{ color: "var(--g-text-muted)", fontSize: "0.8rem" }}>
                  {a.duration_hours}h
                </td>
                <td>
                  <span
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 4,
                      color: "var(--g-text-muted)",
                      fontSize: "0.8rem",
                    }}
                  >
                    <Users size={12} />
                    {a.invite_count}
                  </span>
                </td>
                <td>
                  <span
                    style={{
                      color:
                        a.active_invite_count > 0 ? "var(--g-accent)" : "var(--g-text-muted)",
                      fontSize: "0.8rem",
                    }}
                  >
                    {a.active_invite_count}
                  </span>
                </td>
                <td>
                  <StatusBadge isActive={a.is_active} />
                </td>
                <td>
                  <Link
                    href={`/admin/assessments/${a.id}`}
                    className="g-btn g-btn-ghost g-btn-sm"
                  >
                    Manage
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <AssessmentFormSheet
        open={sheetOpen}
        labs={labs}
        labsLoading={labsLoading}
        saveMutation={createMutation}
        onClose={() => setSheetOpen(false)}
      />
    </div>
  );
}
