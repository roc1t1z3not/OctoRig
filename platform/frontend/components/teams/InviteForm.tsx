"use client";

import { useState } from "react";
import type { TeamRole } from "@/lib/api/teams";

const ROLE_OPTIONS: TeamRole[] = ["manager", "member", "viewer"];

export function InviteForm({
  onSubmit,
  isPending,
  onCancel,
}: {
  onSubmit: (email: string, role: TeamRole) => void;
  isPending: boolean;
  onCancel: () => void;
}) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<TeamRole>("member");

  function handleSubmit() {
    onSubmit(email, role);
    setEmail("");
  }

  return (
    <div className="invite-form">
      <input
        className="g-input g-input-sm"
        placeholder="email@example.com"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        autoFocus
      />
      <select
        className="g-select g-select-sm"
        value={role}
        onChange={(e) => setRole(e.target.value as TeamRole)}
      >
        {ROLE_OPTIONS.map((r) => (
          <option key={r} value={r}>
            {r.charAt(0).toUpperCase() + r.slice(1)}
          </option>
        ))}
      </select>
      <button
        className="g-btn g-btn-primary g-btn-sm"
        onClick={handleSubmit}
        disabled={!email || isPending}
      >
        {isPending ? "Sending…" : "Send"}
      </button>
      <button className="g-btn g-btn-ghost g-btn-sm" onClick={onCancel}>
        Cancel
      </button>
    </div>
  );
}
