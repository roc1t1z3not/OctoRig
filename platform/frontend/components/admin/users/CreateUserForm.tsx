"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { listRoles } from "@/lib/api/admin";

export function CreateUserForm({
  onSubmit,
  isPending,
}: {
  onSubmit: (username: string, email: string, password: string, roles: string[]) => void;
  isPending: boolean;
}) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [roles, setRoles] = useState<string[]>([]);

  const { data: availableRoles = [] } = useQuery({
    queryKey: ["admin-roles"],
    queryFn: listRoles,
  });

  function toggleRole(slug: string) {
    setRoles((r) => (r.includes(slug) ? r.filter((s) => s !== slug) : [...r, slug]));
  }

  function handleSubmit() {
    onSubmit(username, email, password, roles);
    setUsername("");
    setEmail("");
    setPassword("");
    setRoles([]);
  }

  return (
    <div className="g-panel create-panel">
      <div className="g-panel-header">
        <span className="font-mono text-sm">New User</span>
      </div>
      <div className="create-body">
        <div className="form-row">
          <div className="field">
            <label className="text-11 text-muted">Username</label>
            <input
              className="g-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="username"
            />
          </div>
          <div className="field">
            <label className="text-11 text-muted">Email</label>
            <input
              className="g-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@example.com"
            />
          </div>
        </div>
        <div className="form-row">
          <div className="field">
            <label className="text-11 text-muted">Password</label>
            <input
              className="g-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Initial password"
            />
          </div>
          <div className="field checkbox-field">
            <label className="text-11 text-muted">Roles</label>
            {availableRoles.map((role) => (
              <label key={role.slug} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={roles.includes(role.slug)}
                  onChange={() => toggleRole(role.slug)}
                />
                <span className="text-sm">{role.display_name}</span>
              </label>
            ))}
          </div>
        </div>
        <div className="form-actions">
          <button
            className="g-btn g-btn-primary"
            onClick={handleSubmit}
            disabled={!username || !email || !password || isPending}
          >
            {isPending ? "Creating…" : "Create User"}
          </button>
        </div>
      </div>
    </div>
  );
}
