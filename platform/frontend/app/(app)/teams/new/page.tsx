"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "../teams.css";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { createTeam } from "@/lib/api/teams";
import { useNotificationsStore } from "@/stores/notifications.store";

export default function NewTeamPage() {
  const router = useRouter();
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const mutation = useMutation({
    mutationFn: () => createTeam({ name, description: description || undefined }),
    onSuccess: (team) => {
      qc.invalidateQueries({ queryKey: ["teams"] });
      push("success", `Team "${team.name}" created`);
      router.push(`/teams/${team.id}`);
    },
    onError: (err: any) => {
      push("error", err?.response?.data?.detail ?? "Failed to create team");
    },
  });

  return (
    <div className="page">
      <div className="page-header">
        <Link href="/teams" className="back-link text-muted text-sm">
          <ArrowLeft size={14} />
          Teams
        </Link>
      </div>

      <div className="form-card g-panel">
        <div className="g-panel-header">
          <h1 className="font-mono" style={{ fontSize: "0.9375rem" }}>New Team</h1>
        </div>
        <div className="form-body">
          <div className="field">
            <label className="field-label text-11 text-muted">Team Name</label>
            <input
              className="g-input"
              placeholder="e.g. Red Team Alpha"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
          </div>
          <div className="field">
            <label className="field-label text-11 text-muted">Description (optional)</label>
            <textarea
              className="g-input"
              placeholder="What does this team do?"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>
          <div className="form-actions">
            <Link href="/teams" className="g-btn g-btn-ghost">Cancel</Link>
            <button
              className="g-btn g-btn-primary"
              onClick={() => mutation.mutate()}
              disabled={!name.trim() || mutation.isPending}
            >
              {mutation.isPending ? "Creating…" : "Create Team"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
