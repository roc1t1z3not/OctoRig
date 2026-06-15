"use client";

import { useState } from "react";

export function CreateUserForm({
  onSubmit,
  isPending,
}: {
  onSubmit: (username: string, email: string, password: string, isAdmin: boolean) => void;
  isPending: boolean;
}) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);

  function handleSubmit() {
    onSubmit(username, email, password, isAdmin);
    setUsername("");
    setEmail("");
    setPassword("");
    setIsAdmin(false);
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
            <label className="text-11 text-muted">Admin</label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={isAdmin}
                onChange={(e) => setIsAdmin(e.target.checked)}
              />
              <span className="text-sm">Grant admin access</span>
            </label>
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
