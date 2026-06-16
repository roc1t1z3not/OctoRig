// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import type { Rank } from "@/lib/api/ranks";

export function RankChip({ rank }: { rank: Rank | null }) {
  if (!rank) return null;
  return (
    <span
      className="rank-chip"
      style={{ color: rank.color ?? "var(--g-text-muted)", borderColor: rank.color ?? "var(--g-border)" }}
    >
      {rank.name}
    </span>
  );
}
