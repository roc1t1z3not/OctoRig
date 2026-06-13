"use client";

import { useRef, useEffect, useState } from "react";
import { Download, Trash2, Wifi, WifiOff } from "lucide-react";
import { clsx } from "clsx";
import { useLogStream } from "@/hooks/useLogStream";

interface Props {
  deploymentId: number;
  containerNames: string[];
}

export function LogViewer({ deploymentId, containerNames }: Props) {
  const [selectedContainer, setSelectedContainer] = useState("app");
  const bottomRef = useRef<HTMLDivElement>(null);

  // Derive role names from container names (last segment after the final dash)
  const roles = containerNames.map((name) => {
    const parts = name.split("-");
    return parts[parts.length - 1] ?? name;
  });

  const { lines, connected, clearLines } = useLogStream({
    deploymentId,
    container: selectedContainer,
    tail: 100,
    enabled: true,
  });

  // Auto-scroll to bottom on new lines
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  function downloadLogs() {
    const blob = new Blob([lines.join("\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `octorig-${deploymentId}-${selectedContainer}.log`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="log-viewer">
      <div className="log-toolbar">
        {/* Container selector */}
        {roles.length > 1 && (
          <select
            className="g-select"
            value={selectedContainer}
            onChange={(e) => setSelectedContainer(e.target.value)}
          >
            {roles.map((role) => (
              <option key={role} value={role}>{role}</option>
            ))}
          </select>
        )}

        <div className="flex items-center gap-1 ml-auto">
          <span className="flex items-center gap-1 text-10 text-muted">
            {connected
              ? <><Wifi size={12} className="text-success" /> connected</>
              : <><WifiOff size={12} className="text-muted" /> disconnected</>
            }
          </span>
          <button className="g-btn g-btn-ghost g-btn-icon" onClick={clearLines} title="Clear">
            <Trash2 size={14} />
          </button>
          <button className="g-btn g-btn-ghost g-btn-icon" onClick={downloadLogs} title="Download">
            <Download size={14} />
          </button>
        </div>
      </div>

      <div className="log-body">
        {lines.length === 0 ? (
          <span className="log-empty">Waiting for logs…</span>
        ) : (
          lines.map((line, i) => (
            <div key={i} className="log-line">{line}</div>
          ))
        )}
        <div ref={bottomRef} />
      </div>

      <style>{`
        .log-viewer { display: flex; flex-direction: column; height: 100%; }
        .log-toolbar { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; border-bottom: 1px solid var(--g-border); background: var(--g-raised); }
        .log-body { flex: 1; overflow-y: auto; padding: 0.75rem; background: var(--g-code-bg); font-family: var(--font-mono); font-size: 0.7rem; line-height: 1.6; color: var(--g-text-secondary); }
        .log-line { white-space: pre-wrap; word-break: break-all; }
        .log-empty { color: var(--g-text-muted); }
        .ml-auto { margin-left: auto; }
        .flex { display: flex; }
        .items-center { align-items: center; }
        .gap-1 { gap: 0.25rem; }
      `}</style>
    </div>
  );
}
