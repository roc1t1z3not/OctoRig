"use client";
import "../admin.css";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { AlertTriangle, Droplets, RotateCcw, Save, Snowflake } from "lucide-react";
import { useEffect, useState } from "react";
import { resetDatabase } from "@/lib/api/admin";
import {
  getSiteSettings,
  updateSiteSettings,
  type SiteSettings,
} from "@/lib/api/settings";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";
import { useUserStore } from "@/stores/user.store";

export default function AdminSettingsPage() {
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();
  const { user } = useUserStore();
  const router = useRouter();
  const qc = useQueryClient();

  useEffect(() => {
    if (user && !user.is_admin && !user.is_superuser) router.replace("/");
  }, [user, router]);

  const { data: settings, isLoading } = useQuery({
    queryKey: ["site-settings"],
    queryFn: getSiteSettings,
    enabled: !!(user?.is_admin || user?.is_superuser),
  });

  const [platform, setPlatform] = useState<Partial<SiteSettings>>({});
  const [scoring, setScoring] = useState<Partial<SiteSettings>>({});

  useEffect(() => {
    if (!settings) return;
    setPlatform({
      registration_open: settings.registration_open,
      maintenance_mode: settings.maintenance_mode,
      maintenance_message: settings.maintenance_message,
      max_flag_attempts: settings.max_flag_attempts,
    });
    setScoring({
      dynamic_scoring_enabled: settings.dynamic_scoring_enabled,
      dynamic_decay_factor: settings.dynamic_decay_factor,
      dynamic_min_floor_pct: settings.dynamic_min_floor_pct,
      scoreboard_frozen_at: settings.scoreboard_frozen_at,
      first_blood_enabled: settings.first_blood_enabled,
    });
  }, [settings]);

  const saveMutation = useMutation({
    mutationFn: updateSiteSettings,
    onSuccess: () => {
      push("success", "Settings saved");
      qc.invalidateQueries({ queryKey: ["site-settings"] });
    },
    onError: () => push("error", "Failed to save settings"),
  });

  const resetDbMutation = useMutation({
    mutationFn: resetDatabase,
    onSuccess: () => push("success", "Database reset — all activity data cleared"),
    onError: () => push("error", "Failed to reset database"),
  });

  function handleResetDb() {
    confirm({
      title: "Reset entire database?",
      body: "This will permanently delete ALL challenge submissions, scores, hint unlocks, deployments, and audit logs for every user. Lab templates, challenges, and accounts are kept. This cannot be undone.",
      confirmLabel: "Reset Database",
      dangerous: true,
      onConfirm: () => resetDbMutation.mutate(),
    });
  }

  // Convert local datetime string to ISO for API
  function toISOOrNull(val: string | null | undefined): string | null {
    if (!val) return null;
    try { return new Date(val).toISOString(); } catch { return null; }
  }

  // Convert ISO to datetime-local input format
  function toLocalInput(val: string | null | undefined): string {
    if (!val) return "";
    try {
      const d = new Date(val);
      return d.toISOString().slice(0, 16);
    } catch { return ""; }
  }

  if (isLoading || !settings) {
    return (
      <div className="page">
        <div className="page-header"><h1 className="page-title font-mono">Settings</h1></div>
        <p style={{ color: "var(--g-text-muted)", fontSize: "0.875rem" }}>Loading…</p>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Settings</h1>
      </div>

      {/* ── PLATFORM ───────────────────────────────────────────────────────── */}
      <section className="settings-section">
        <h2 className="settings-section-title">Platform</h2>

        <div className="settings-row">
          <div className="settings-row-info">
            <span className="settings-row-label">Open Registration</span>
            <span className="settings-row-desc">
              Allow new users to self-register at <code>/register</code>. Disable to lock down signups.
            </span>
          </div>
          <label className="toggle">
            <input
              type="checkbox"
              checked={platform.registration_open ?? true}
              onChange={(e) => setPlatform((p) => ({ ...p, registration_open: e.target.checked }))}
            />
            <span className="toggle-track" />
          </label>
        </div>

        <div className="settings-row">
          <div className="settings-row-info">
            <span className="settings-row-label">Maintenance Mode</span>
            <span className="settings-row-desc">
              Show a maintenance screen to all non-admin users. Admins see a banner and can still
              access everything.
            </span>
          </div>
          <label className="toggle">
            <input
              type="checkbox"
              checked={platform.maintenance_mode ?? false}
              onChange={(e) => setPlatform((p) => ({ ...p, maintenance_mode: e.target.checked }))}
            />
            <span className="toggle-track" />
          </label>
        </div>

        {platform.maintenance_mode && (
          <div className="settings-row settings-row--indent">
            <div className="settings-row-info">
              <span className="settings-row-label">Maintenance Message</span>
              <span className="settings-row-desc">Shown to users on the maintenance screen.</span>
            </div>
            <textarea
              className="g-input"
              style={{ width: 280, height: 72, resize: "vertical" }}
              placeholder="We'll be back shortly."
              value={platform.maintenance_message ?? ""}
              onChange={(e) =>
                setPlatform((p) => ({ ...p, maintenance_message: e.target.value || null }))
              }
            />
          </div>
        )}

        <div className="settings-row">
          <div className="settings-row-info">
            <span className="settings-row-label">Max Flag Attempts</span>
            <span className="settings-row-desc">
              Maximum wrong flag submissions per challenge (global default). Leave blank for
              unlimited.
            </span>
          </div>
          <input
            type="number"
            className="g-input"
            style={{ width: 100, textAlign: "right" }}
            min={1}
            placeholder="∞"
            value={platform.max_flag_attempts ?? ""}
            onChange={(e) =>
              setPlatform((p) => ({
                ...p,
                max_flag_attempts: e.target.value ? parseInt(e.target.value) : null,
              }))
            }
          />
        </div>

        <div className="settings-row-actions">
          <button
            className="g-btn g-btn-primary g-btn-sm"
            disabled={saveMutation.isPending}
            onClick={() => saveMutation.mutate(platform)}
          >
            <Save size={13} />
            Save Platform Settings
          </button>
        </div>
      </section>

      {/* ── SCORING ────────────────────────────────────────────────────────── */}
      <section className="settings-section">
        <h2 className="settings-section-title">Scoring</h2>

        <div className="settings-row">
          <div className="settings-row-info">
            <span className="settings-row-label">First Blood</span>
            <span className="settings-row-desc">
              Track and display who was the first solver on each challenge.
            </span>
          </div>
          <label className="toggle">
            <input
              type="checkbox"
              checked={scoring.first_blood_enabled ?? true}
              onChange={(e) => setScoring((s) => ({ ...s, first_blood_enabled: e.target.checked }))}
            />
            <span className="toggle-track" />
          </label>
        </div>

        <div className="settings-row">
          <div className="settings-row-info">
            <span className="settings-row-label">
              <Droplets size={13} style={{ display: "inline", marginRight: 4, verticalAlign: "middle" }} />
              Dynamic Scoring
            </span>
            <span className="settings-row-desc">
              Points decrease as more players solve a challenge. First blood gets full points.
            </span>
          </div>
          <label className="toggle">
            <input
              type="checkbox"
              checked={scoring.dynamic_scoring_enabled ?? false}
              onChange={(e) =>
                setScoring((s) => ({ ...s, dynamic_scoring_enabled: e.target.checked }))
              }
            />
            <span className="toggle-track" />
          </label>
        </div>

        {scoring.dynamic_scoring_enabled && (
          <>
            <div className="settings-row settings-row--indent">
              <div className="settings-row-info">
                <span className="settings-row-label">Decay Factor</span>
                <span className="settings-row-desc">
                  Multiplier per solve (0.0–1.0). Lower = faster decay. Default 0.9.
                </span>
              </div>
              <input
                type="number"
                className="g-input"
                style={{ width: 100, textAlign: "right" }}
                min={0}
                max={1}
                step={0.05}
                value={scoring.dynamic_decay_factor ?? 0.9}
                onChange={(e) =>
                  setScoring((s) => ({ ...s, dynamic_decay_factor: parseFloat(e.target.value) }))
                }
              />
            </div>
            <div className="settings-row settings-row--indent">
              <div className="settings-row-info">
                <span className="settings-row-label">Minimum Floor (%)</span>
                <span className="settings-row-desc">
                  Points never drop below this percentage of the base value. Default 10%.
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <input
                  type="number"
                  className="g-input"
                  style={{ width: 80, textAlign: "right" }}
                  min={1}
                  max={100}
                  value={scoring.dynamic_min_floor_pct ?? 10}
                  onChange={(e) =>
                    setScoring((s) => ({
                      ...s,
                      dynamic_min_floor_pct: parseInt(e.target.value),
                    }))
                  }
                />
                <span style={{ color: "var(--g-text-muted)", fontSize: "0.8125rem" }}>%</span>
              </div>
            </div>
          </>
        )}

        <div className="settings-row">
          <div className="settings-row-info">
            <span className="settings-row-label">
              <Snowflake size={13} style={{ display: "inline", marginRight: 4, verticalAlign: "middle" }} />
              Freeze Scoreboard At
            </span>
            <span className="settings-row-desc">
              Lock the global leaderboard display at this time. New solves still record but won&apos;t
              move rankings.
            </span>
          </div>
          <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <input
              type="datetime-local"
              className="g-input"
              style={{ width: 200 }}
              value={toLocalInput(scoring.scoreboard_frozen_at)}
              onChange={(e) =>
                setScoring((s) => ({
                  ...s,
                  scoreboard_frozen_at: toISOOrNull(e.target.value),
                }))
              }
            />
            {scoring.scoreboard_frozen_at && (
              <button
                className="g-btn g-btn-ghost g-btn-sm"
                onClick={() => setScoring((s) => ({ ...s, scoreboard_frozen_at: null }))}
              >
                Clear
              </button>
            )}
          </div>
        </div>

        <div className="settings-row-actions">
          <button
            className="g-btn g-btn-primary g-btn-sm"
            disabled={saveMutation.isPending}
            onClick={() => saveMutation.mutate(scoring)}
          >
            <Save size={13} />
            Save Scoring Settings
          </button>
        </div>
      </section>

      {/* ── DANGER ZONE ─────────────────────────────────────────────────────── */}
      <div className="danger-zone">
        <div className="danger-zone-header">
          <AlertTriangle size={14} />
          <span>Danger Zone</span>
        </div>

        <div className="danger-action">
          <div className="danger-action-info">
            <span className="danger-action-title">Reset Database</span>
            <span className="danger-action-desc">
              Wipe all user activity — submissions, scores, hint unlocks, deployments, and audit
              logs. Accounts, teams, labs, and challenges are preserved.
            </span>
          </div>
          <button
            className="g-btn g-btn-danger"
            disabled={resetDbMutation.isPending}
            onClick={handleResetDb}
          >
            <RotateCcw size={13} />
            {resetDbMutation.isPending ? "Resetting…" : "Reset Database"}
          </button>
        </div>
      </div>

      <style>{`
        .settings-section {
          background: var(--g-surface);
          border: 1px solid var(--g-border);
          border-radius: 8px;
          overflow: hidden;
          margin-top: 1.5rem;
        }
        .settings-section-title {
          font-size: 0.6875rem;
          font-weight: 700;
          font-family: var(--font-mono, monospace);
          text-transform: uppercase;
          letter-spacing: 0.08em;
          color: var(--g-text-muted);
          padding: 0.625rem 1rem;
          border-bottom: 1px solid var(--g-border);
          margin: 0;
        }
        .settings-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1.5rem;
          padding: 0.875rem 1rem;
          border-bottom: 1px solid var(--g-border);
        }
        .settings-row:last-of-type { border-bottom: none; }
        .settings-row--indent { padding-left: 2rem; background: color-mix(in srgb, var(--g-border) 30%, transparent); }
        .settings-row-info { display: flex; flex-direction: column; gap: 0.2rem; flex: 1; }
        .settings-row-label { font-size: 0.8125rem; font-weight: 600; color: var(--g-text); }
        .settings-row-desc { font-size: 0.75rem; color: var(--g-text-muted); line-height: 1.4; max-width: 480px; }
        .settings-row-actions { padding: 0.75rem 1rem; display: flex; justify-content: flex-end; border-top: 1px solid var(--g-border); }
        /* Toggle */
        .toggle { position: relative; display: inline-flex; cursor: pointer; flex-shrink: 0; }
        .toggle input { opacity: 0; width: 0; height: 0; position: absolute; }
        .toggle-track {
          width: 38px; height: 22px;
          background: var(--g-border);
          border-radius: 11px;
          transition: background 0.18s;
          position: relative;
        }
        .toggle-track::after {
          content: "";
          position: absolute;
          top: 3px; left: 3px;
          width: 16px; height: 16px;
          border-radius: 50%;
          background: #fff;
          transition: transform 0.18s;
        }
        .toggle input:checked ~ .toggle-track { background: var(--g-accent); }
        .toggle input:checked ~ .toggle-track::after { transform: translateX(16px); }
        /* Danger zone */
        .danger-zone {
          border: 1px solid var(--g-danger);
          border-radius: 8px;
          overflow: hidden;
          margin-top: 1.5rem;
        }
        .danger-zone-header {
          display: flex; align-items: center; gap: 0.5rem;
          padding: 0.625rem 1rem;
          background: color-mix(in srgb, var(--g-danger) 10%, transparent);
          color: var(--g-danger);
          font-size: 0.6875rem; font-weight: 700;
          font-family: var(--font-mono, monospace);
          text-transform: uppercase; letter-spacing: 0.08em;
          border-bottom: 1px solid color-mix(in srgb, var(--g-danger) 30%, transparent);
        }
        .danger-action {
          display: flex; align-items: center; justify-content: space-between;
          gap: 1.5rem; padding: 1rem;
        }
        .danger-action-info { display: flex; flex-direction: column; gap: 0.25rem; }
        .danger-action-title { font-size: 0.8125rem; font-weight: 600; color: var(--g-text); }
        .danger-action-desc { font-size: 0.75rem; color: var(--g-text-muted); line-height: 1.5; max-width: 480px; }
      `}</style>
    </div>
  );
}
