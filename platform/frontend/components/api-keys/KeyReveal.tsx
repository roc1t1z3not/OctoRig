"use client";

import { useState } from "react";
import { Copy, Check } from "lucide-react";
import type { ApiKeyCreated } from "@/lib/api/apiKeys";

export function KeyReveal({ createdKey, onDismiss }: { createdKey: ApiKeyCreated; onDismiss: () => void }) {
  const [copied, setCopied] = useState(false);

  async function copyKey() {
    await navigator.clipboard.writeText(createdKey.raw_key);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="key-reveal g-panel">
      <div className="g-panel-header">
        <span className="text-success font-mono text-sm">Key created — copy it now</span>
      </div>
      <div className="key-reveal-body">
        <p className="text-muted text-11">
          This is the only time your full API key will be shown. Store it securely.
        </p>
        <div className="key-display">
          <code className="key-value font-mono text-sm">{createdKey.raw_key}</code>
          <button
            className="g-btn g-btn-ghost g-btn-icon"
            onClick={copyKey}
            title="Copy key"
          >
            {copied ? <Check size={14} className="text-success" /> : <Copy size={14} />}
          </button>
        </div>
        <button className="g-btn g-btn-ghost g-btn-sm mt-2" onClick={onDismiss}>
          I&apos;ve saved my key
        </button>
      </div>
    </div>
  );
}
