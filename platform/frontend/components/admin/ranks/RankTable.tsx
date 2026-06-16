// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Pencil, Trash2 } from "lucide-react";
import type { Rank } from "@/lib/api/ranks";
import { RankChip } from "@/components/ui/RankChip";

export function RankTable({
  ranks,
  selected,
  isLoading,
  onEdit,
  onDelete,
}: {
  ranks: Rank[];
  selected: Rank | null;
  isLoading: boolean;
  onEdit: (rank: Rank) => void;
  onDelete: (rank: Rank) => void;
}) {
  if (isLoading) {
    return <div className="text-muted text-sm" style={{ padding: "1rem" }}>Loading…</div>;
  }

  return (
    <table className="rank-table">
      <thead>
        <tr>
          <th>Rank</th>
          <th>Icon</th>
          <th>Min Points</th>
          <th>Status</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {ranks.map((rank) => (
          <tr
            key={rank.id}
            className={selected?.id === rank.id ? "selected" : ""}
            style={{ cursor: "pointer" }}
            onClick={() => onEdit(rank)}
          >
            <td>
              <RankChip rank={rank} />
            </td>
            <td style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem" }}>
              {rank.icon || "—"}
            </td>
            <td className="rank-pts">{rank.min_points.toLocaleString()}</td>
            <td>
              <span
                className="inactive-pill"
                style={rank.is_active ? { background: "var(--g-accent-dim)", color: "var(--g-accent)" } : undefined}
              >
                {rank.is_active ? "active" : "inactive"}
              </span>
            </td>
            <td>
              <div style={{ display: "flex", gap: "0.4rem" }} onClick={(e) => e.stopPropagation()}>
                <button
                  className="g-btn g-btn-ghost"
                  style={{ padding: "0.2rem 0.4rem" }}
                  onClick={() => onEdit(rank)}
                  title="Edit"
                >
                  <Pencil size={12} />
                </button>
                <button
                  className="g-btn g-btn-ghost"
                  style={{ padding: "0.2rem 0.4rem", color: "var(--g-danger)" }}
                  onClick={() => onDelete(rank)}
                  title="Delete"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
