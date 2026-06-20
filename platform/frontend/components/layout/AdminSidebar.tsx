"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ShieldCheck, UserCog, FolderGit2, Container, ScrollText,
  Trophy, Flag, KeyRound, BarChart3, Zap, ClipboardList, Settings,
  ArrowLeft, LogOut, Boxes,
} from "lucide-react";
import { clsx } from "clsx";
import { useUserStore } from "@/stores/user.store";
import { useThemeStore } from "@/stores/theme.store";
import { logout } from "@/lib/api/auth";
import { Brand } from "./Brand";

const NAV_ADMIN = [
  { href: "/admin",              icon: ShieldCheck,   label: "Overview" },
  { href: "/admin/users",        icon: UserCog,       label: "Users" },
  { href: "/admin/roles",        icon: ShieldCheck,   label: "Roles" },
  { href: "/admin/teams",        icon: FolderGit2,    label: "Teams" },
  { href: "/admin/labs",         icon: Boxes,         label: "Labs" },
  { href: "/admin/deployments",  icon: Container,     label: "Deployments" },
  { href: "/admin/audit",        icon: ScrollText,    label: "Audit Log" },
  { href: "/admin/challenges",   icon: Trophy,        label: "Challenges" },
  { href: "/admin/events",       icon: Flag,          label: "Events" },
  { href: "/admin/api-keys",     icon: KeyRound,      label: "API Keys" },
  { href: "/admin/ranks",        icon: BarChart3,     label: "Ranks" },
  { href: "/admin/assessments",  icon: Zap,           label: "Assessments" },
  { href: "/admin/content",      icon: ClipboardList, label: "Content" },
  { href: "/admin/settings",     icon: Settings,      label: "Settings" },
];

export function AdminSidebar() {
  const pathname = usePathname();
  const { user, clearSession } = useUserStore();
  const { resetExplicit } = useThemeStore();

  function isActive(href: string) {
    if (href === "/admin") return pathname === "/admin";
    return pathname.startsWith(href);
  }

  async function handleLogout() {
    try { await logout(); } catch {}
    resetExplicit();
    clearSession();
    window.location.href = "/login";
  }

  return (
    <aside
      className="w-52 shrink-0 flex flex-col h-full border-r"
      style={{ background: "var(--g-chrome)", borderColor: "var(--g-border)" }}
    >
      <div className="px-4 pt-2">
        <Brand />
      </div>
      {/* Back to platform */}
      <div className="p-2 border-b shrink-0" style={{ borderColor: "var(--g-border)" }}>
        <Link
          href="/"
          className="g-nav-item"
        >
          <ArrowLeft size={14} className="shrink-0" style={{ color: "var(--g-text-muted)" }} />
          <span style={{ color: "var(--g-text-muted)" }}>Back to Platform</span>
        </Link>
      </div>

      <div className="px-3 pt-3 pb-1 shrink-0">
        <span
          className="text-9px font-mono uppercase"
          style={{ color: "var(--g-text-muted)", letterSpacing: "0.12em" }}
        >
          Admin
        </span>
      </div>

      {/* Admin nav */}
      <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto">
        {NAV_ADMIN.map(({ href, icon: Icon, label }) => {
          const active = isActive(href);
          return (
            <Link
              key={href}
              href={href}
              className={clsx("g-nav-item", active && "active")}
              style={active ? {
                background: "var(--g-accent-dim)",
                color: "var(--g-text)",
                borderColor: "var(--g-border-hover)",
              } : undefined}
              title={label}
            >
              <Icon
                size={14}
                className="shrink-0"
                style={{ color: active ? "var(--g-accent)" : "var(--g-text-muted)" }}
              />
              <span style={{ color: active ? "var(--g-text)" : "var(--g-text-muted)" }}>
                {label}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* Footer — username + logout */}
      <div
        className="border-t shrink-0 flex items-center justify-between px-3 py-2"
        style={{ borderColor: "var(--g-border)" }}
      >
        <span className="text-11 font-mono truncate" style={{ color: "var(--g-text)" }}>
          {user?.username ?? "—"}
        </span>
        <button
          onClick={handleLogout}
          title="Log out"
          className="flex items-center justify-center p-1 rounded hover:bg-[var(--g-accent-dim)] transition-colors"
          style={{ color: "var(--g-danger, #f85149)" }}
        >
          <LogOut size={13} />
        </button>
      </div>
    </aside>
  );
}
