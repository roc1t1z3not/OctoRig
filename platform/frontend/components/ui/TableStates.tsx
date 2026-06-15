export function LoadingCell() {
  return <div className="loading-cell text-muted text-sm">Loading…</div>;
}

export function EmptyCell({ label }: { label: string }) {
  return <div className="empty-cell text-muted text-sm">{label}</div>;
}
