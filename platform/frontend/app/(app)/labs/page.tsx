"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./labs.css";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { getLabs } from "@/lib/api/labs";
import { stopDeployment, resetDeployment } from "@/lib/api/deployments";
import { LabCard } from "@/components/labs/LabCard";
import { useNotificationsStore } from "@/stores/notifications.store";
import { PageSpinner } from "@/components/ui/Spinner";

const CATEGORIES = [
  { id: undefined, label: "All" },
  { id: "world", label: "World" },
  { id: "firerange", label: "Fire Range" },
  { id: "thirdparty", label: "Third Party" },
] as const;

export default function LabsPage() {
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [search, setSearch] = useState("");
  const qc = useQueryClient();
  const { push } = useNotificationsStore();

  const { data: labs = [], isLoading } = useQuery({
    queryKey: ["labs", category],
    queryFn: () => getLabs(category),
  });

  const stopMutation = useMutation({
    mutationFn: stopDeployment,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["labs"] }); push("success", "Lab stop requested"); },
    onError: () => push("error", "Failed to stop lab"),
  });

  const resetMutation = useMutation({
    mutationFn: resetDeployment,
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["labs"] }); push("success", "Lab reset requested"); },
    onError: () => push("error", "Failed to reset lab"),
  });

  const filtered = labs.filter((l) =>
    search === "" || l.name.toLowerCase().includes(search.toLowerCase()) || l.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="page">
      <h1 className="page-title font-mono">Lab Catalog</h1>

      {/* Filter bar */}
      <div className="filter-bar">
        <div className="g-input-icon">
          <Search size={14} className="icon-left" />
          <input
            className="g-input"
            placeholder="Search labs…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-1">
          {CATEGORIES.map((c) => (
            <button
              key={String(c.id)}
              className={`g-btn ${category === c.id ? "g-btn-primary" : "g-btn-ghost"}`}
              onClick={() => setCategory(c.id)}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <PageSpinner />
      ) : (
        <div className="labs-grid mt-4">
          {filtered.map((lab) => (
            <LabCard
              key={lab.id}
              lab={lab}
              onStop={stopMutation.mutate}
              onReset={resetMutation.mutate}
            />
          ))}
          {filtered.length === 0 && (
            <div className="text-muted text-sm">No labs match your filter.</div>
          )}
        </div>
      )}
    </div>
  );
}
