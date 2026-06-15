export function BodyPreview({
  body,
  contentType,
}: {
  body: Record<string, unknown>;
  contentType: string;
}) {
  const isEmpty = Object.keys(body).length === 0;
  return (
    <div style={{
      background: "var(--g-surface)", border: "1px solid var(--g-border)",
      borderRadius: "4px", padding: "0.75rem",
    }}>
      <div style={{ fontSize: "0.625rem", textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--g-text-muted)", marginBottom: "0.5rem" }}>
        Body
      </div>
      {isEmpty ? (
        <span style={{ fontSize: "0.75rem", color: "var(--g-text-muted)", fontStyle: "italic" }}>No body content.</span>
      ) : contentType === "challenge" ? (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.3rem", fontSize: "0.8125rem" }}>
          {[
            ["Difficulty", body.difficulty],
            ["Category", body.category],
            ["Type", body.challenge_type],
            ["Points", body.points ?? 100],
          ].map(([label, val]) => (
            <div key={String(label)}>
              <span style={{ color: "var(--g-text-muted)", marginRight: "0.4rem" }}>{String(label)}:</span>
              <span style={{ color: "var(--g-text)" }}>{String(val ?? "—")}</span>
            </div>
          ))}
          <div>
            <span style={{ color: "var(--g-text-muted)", marginRight: "0.4rem" }}>Description:</span>
            <span style={{ color: "var(--g-text)" }}>{String(body.description ?? "—")}</span>
          </div>
          {Array.isArray(body.flags) && body.flags.length > 0 && (
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.25rem", alignItems: "center" }}>
              <span style={{ color: "var(--g-text-muted)", marginRight: "0.2rem" }}>Flags ({(body.flags as any[]).length}):</span>
              {(body.flags as any[]).map((f: any, i: number) => (
                <code key={i} style={{ background: "var(--g-surface-2)", padding: "0.1rem 0.35rem", borderRadius: "3px", fontSize: "0.75rem" }}>
                  {f.value} ({f.flag_type ?? "static"})
                </code>
              ))}
            </div>
          )}
          {Array.isArray(body.hints) && (body.hints as any[]).length > 0 && (
            <div>
              <span style={{ color: "var(--g-text-muted)", marginRight: "0.4rem" }}>Hints:</span>
              <span style={{ color: "var(--g-text)" }}>{(body.hints as any[]).length}</span>
            </div>
          )}
        </div>
      ) : (
        <pre style={{ margin: 0, fontSize: "0.75rem", color: "var(--g-text-secondary)", whiteSpace: "pre-wrap", wordBreak: "break-all", fontFamily: "var(--font-mono, monospace)" }}>
          {JSON.stringify(body, null, 2)}
        </pre>
      )}
    </div>
  );
}
