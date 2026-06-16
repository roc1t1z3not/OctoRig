"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import "./login.css";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { login, getMe } from "@/lib/api/auth";
import { useUserStore } from "@/stores/user.store";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { setSession, accessToken } = useUserStore();
  const router = useRouter();

  useEffect(() => {
    if (accessToken) router.replace("/");
  }, [accessToken, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const token = await login(username, password);
      // Temporarily set token so getMe() can use the interceptor
      useUserStore.getState().setAccessToken(token.access_token);
      const user = await getMe();
      setSession(user, token.access_token);
      router.replace("/");
    } catch {
      setError("Invalid username or password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <div className="g-card login-card">
        <div className="login-brand">
          <span style={{ color: "var(--g-accent)" }}>OCTO</span>
          <span style={{ color: "var(--g-text)" }}>RIG</span>
        </div>

        <form onSubmit={handleSubmit} className="login-form mt-4">
          <input
            className="g-input"
            type="text"
            placeholder="Username"
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            className="g-input"
            type="password"
            placeholder="Password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <p className="text-danger text-11">{error}</p>}
          <button className="g-btn g-btn-primary w-full" type="submit" disabled={loading}>
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}
