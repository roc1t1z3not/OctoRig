// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { Save } from "lucide-react";
import type { SiteSettings } from "@/lib/api/settings";
import { SettingToggle } from "./SettingToggle";

export function FeaturesSection({
  features,
  onChange,
  onSave,
  isPending,
}: {
  features: Partial<SiteSettings>;
  onChange: (patch: Partial<SiteSettings>) => void;
  onSave: () => void;
  isPending: boolean;
}) {
  return (
    <section className="settings-section">
      <h2 className="settings-section-title">Features</h2>

      <SettingToggle
        label="Python Editor"
        description="Show an in-browser Python scratchpad on Python challenges. Runs entirely in the user's browser via Pyodide (WebAssembly) — nothing reaches the server."
        checked={features.python_editor_enabled ?? true}
        onChange={(v) => onChange({ python_editor_enabled: v })}
      />

      <div className="settings-row-actions">
        <button
          className="g-btn g-btn-primary g-btn-sm"
          disabled={isPending}
          onClick={onSave}
        >
          <Save size={13} />
          Save Feature Settings
        </button>
      </div>
    </section>
  );
}
