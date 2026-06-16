"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./settings.css";

import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Palette, User, Shield } from "lucide-react";
import { changePassword, getMe } from "@/lib/api/auth";
import { useThemeStore } from "@/stores/theme.store";
import { useUserStore } from "@/stores/user.store";
import { useNotificationsStore } from "@/stores/notifications.store";
import { THEMES } from "@/lib/themes";

export default function SettingsPage() {
  const { theme, setTheme } = useThemeStore();
  const { user } = useUserStore();
  const { push } = useNotificationsStore();
  const [section, setSection] = useState<"appearance" | "account">("appearance");

  const { data: me } = useQuery({ queryKey: ["me"], queryFn: getMe });

  return (
    <div className="page">
      <h1 className="page-title font-mono">Settings</h1>

      <div className="settings-layout">
        <nav className="settings-nav g-panel">
          {([
            { id: "appearance", label: "Appearance", icon: <Palette size={15} /> },
            { id: "account",    label: "Account",    icon: <User size={15} /> },
          ] as const).map((item) => (
            <button
              key={item.id}
              className={`settings-nav-item ${section === item.id ? "active" : ""}`}
              onClick={() => setSection(item.id)}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </nav>

        <div className="settings-content g-panel">
          {section === "appearance" && (
            <div>
              <h2 className="settings-section-title font-mono">Theme</h2>
              <p className="text-muted text-sm mb-3">Choose a color theme for the platform.</p>
              <div className="theme-grid">
                {THEMES.map((t) => (
                  <button
                    key={t.id}
                    className={`theme-card ${theme === t.id ? "active" : ""}`}
                    onClick={() => setTheme(t.id)}
                    aria-pressed={theme === t.id}
                  >
                    <div className="theme-swatches">
                      {[t.preview.bg, t.preview.accent, t.preview.text].map((color, i) => (
                        <div key={i} className="theme-swatch" style={{ background: color }} />
                      ))}
                    </div>
                    <span className="theme-name text-11 font-mono">{t.name}</span>
                    {theme === t.id && <span className="theme-active-dot" />}
                  </button>
                ))}
              </div>
            </div>
          )}

          {section === "account" && (
            <div className="settings-section">
              <h2 className="settings-section-title font-mono">Account</h2>
              <div className="meta-rows">
                <MetaRow label="Username" value={me?.username ?? user?.username ?? "—"} />
                <MetaRow label="Email" value={me?.email ?? user?.email ?? "—"} />
                <MetaRow
                  label="Role"
                  value={(me?.is_superuser ?? user?.is_superuser) ? "Administrator" : "User"}
                />
              </div>
              {(me?.is_superuser ?? user?.is_superuser) && (
                <div className="admin-notice mt-3">
                  <Shield size={13} />
                  <span className="text-11 text-warning">Administrator account — full platform access</span>
                </div>
              )}

              <hr className="settings-divider" />

              <h2 className="settings-section-title font-mono">Change Password</h2>
              <ChangePasswordForm push={push} />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="meta-row">
      <span className="text-muted text-11">{label}</span>
      <span className="text-sm text-secondary">{value}</span>
    </div>
  );
}

function ChangePasswordForm({ push }: { push: (type: "success" | "error", msg: string) => void }) {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");

  const mutation = useMutation({
    mutationFn: () => changePassword(current, next),
    onSuccess: () => {
      push("success", "Password changed");
      setCurrent(""); setNext(""); setConfirm("");
    },
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Failed to change password";
      push("error", msg);
    },
  });

  const mismatch = next !== confirm && confirm.length > 0;
  const canSubmit = current && next && next === confirm && next.length >= 8;

  return (
    <form
      className="pw-form"
      onSubmit={(e) => { e.preventDefault(); if (canSubmit) mutation.mutate(); }}
    >
      <div className="settings-field">
        <label>Current password</label>
        <input
          type="password"
          className="g-input"
          value={current}
          onChange={(e) => setCurrent(e.target.value)}
          autoComplete="current-password"
        />
      </div>
      <div className="settings-field">
        <label>New password <span className="text-muted">(min 8 chars)</span></label>
        <input
          type="password"
          className="g-input"
          value={next}
          onChange={(e) => setNext(e.target.value)}
          autoComplete="new-password"
        />
      </div>
      <div className="settings-field">
        <label>Confirm new password</label>
        <input
          type="password"
          className={`g-input ${mismatch ? "input-error" : ""}`}
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          autoComplete="new-password"
        />
        {mismatch && <span className="input-hint text-danger text-11">Passwords don't match</span>}
      </div>
      <div className="settings-field" style={{ alignItems: "flex-start" }}>
        <button
          type="submit"
          className="g-btn g-btn-primary"
          disabled={!canSubmit || mutation.isPending}
        >
          {mutation.isPending ? "Saving…" : "Update Password"}
        </button>
      </div>
    </form>
  );
}
