export function Spinner({ size = 18 }: { size?: number }) {
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        border: "2px solid var(--g-border)",
        borderTopColor: "var(--g-accent)",
        animation: "spin 0.75s linear infinite",
        flexShrink: 0,
      }}
    />
  );
}

export function PageSpinner() {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "2rem 0" }}>
      <Spinner />
      <span style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>Loading…</span>
    </div>
  );
}
