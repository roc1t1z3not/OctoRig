// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
export function LoadingCell() {
  return <div className="loading-cell text-muted text-sm">Loading…</div>;
}

export function EmptyCell({ label }: { label: string }) {
  return <div className="empty-cell text-muted text-sm">{label}</div>;
}
