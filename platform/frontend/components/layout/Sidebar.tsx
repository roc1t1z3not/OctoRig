"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useRef, useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  LayoutDashboard, FlaskConical, Rocket, Settings, LogOut, Users,
  KeyRound, ShieldCheck, UserCog, FolderGit2, Container, ScrollText,
  Swords, Flag, Award, ChevronUp, Zap, PenTool, User, ClipboardList, Trophy,
  BarChart3,
} from "lucide-react";
import { getMyRank } from "@/lib/api/ranks";
import { clsx } from "clsx";
import { useUserStore } from "@/stores/user.store";
import { logout } from "@/lib/api/auth";
import { getMyProfile } from "@/lib/api/profiles";

const NAV_MAIN = [
  { href: "/",             icon: LayoutDashboard, label: "Dashboard" },
  { href: "/challenges",   icon: Swords,          label: "Challenges" },
  { href: "/events",       icon: Flag,            label: "Events" },
  { href: "/scoreboard",   icon: Trophy,          label: "Scoreboard" },
  { href: "/badges",       icon: Award,           label: "Badges" },
  { href: "/labs",         icon: FlaskConical,    label: "Labs" },
  { href: "/deployments",  icon: Rocket,          label: "Deployments" },
  { href: "/teams",        icon: Users,           label: "Teams" },
  { href: "/api-keys",     icon: KeyRound,        label: "API Keys" },
];

const NAV_ADMIN = [
  { href: "/admin",              icon: ShieldCheck,   label: "Overview" },
  { href: "/admin/users",        icon: UserCog,       label: "Users" },
  { href: "/admin/teams",        icon: FolderGit2,    label: "Teams" },
  { href: "/admin/deployments",  icon: Container,     label: "Deployments" },
  { href: "/admin/audit",        icon: ScrollText,    label: "Audit Log" },
  { href: "/admin/challenges",   icon: Trophy,        label: "Challenges" },
  { href: "/admin/events",       icon: Flag,          label: "Events" },
  { href: "/admin/api-keys",     icon: KeyRound,      label: "API Keys" },
  { href: "/admin/ranks",        icon: BarChart3,     label: "Ranks" },
  { href: "/admin/content",      icon: ClipboardList, label: "Content" },
  { href: "/admin/settings",     icon: Settings,      label: "Settings" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, clearSession } = useUserStore();
  const isPrivileged = user?.is_admin || user?.is_superuser;
  const [menuOpen, setMenuOpen] = useState(false);
  const [adminOpen, setAdminOpen] = useState(() => pathname.startsWith("/admin"));
  const menuRef = useRef<HTMLDivElement>(null);

  const { data: profile } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: getMyProfile,
    staleTime: 60_000,
  });

  const { data: myRank } = useQuery({
    queryKey: ["rank", "me"],
    queryFn: getMyRank,
    staleTime: 60_000,
    enabled: !!user,
  });

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, [menuOpen]);

  async function handleLogout() {
    try { await logout(); } catch {}
    clearSession();
    window.location.href = "/login";
  }

  function isActive(href: string) {
    if (href === "/") return pathname === "/";
    if (href === "/admin") return pathname === "/admin";
    return pathname.startsWith(href);
  }

  return (
    <aside
      className="w-52 shrink-0 flex flex-col h-full border-r"
      style={{ background: "var(--g-chrome)", borderColor: "var(--g-border)" }}
    >

      {/* Main nav */}
      <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto">
        {NAV_MAIN.map(({ href, icon: Icon, label }) => {
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
        {(user?.is_admin || user?.platform_roles?.includes("creator")) && (() => {
          const active = isActive("/creator");
          return (
            <Link
              href="/creator"
              className={clsx("g-nav-item", active && "active")}
              style={active ? {
                background: "var(--g-accent-dim)",
                color: "var(--g-text)",
                borderColor: "var(--g-border-hover)",
              } : undefined}
              title="Creator"
            >
              <PenTool
                size={14}
                className="shrink-0"
                style={{ color: active ? "var(--g-accent)" : "var(--g-text-muted)" }}
              />
              <span style={{ color: active ? "var(--g-text)" : "var(--g-text-muted)" }}>
                Creator
              </span>
            </Link>
          );
        })()}
      </nav>

      {/* Admin nav */}
      {isPrivileged && (
        <div className="p-2 border-t shrink-0" style={{ borderColor: "var(--g-border)" }}>
          <button
            onClick={() => setAdminOpen((o) => !o)}
            className="w-full flex items-center justify-between px-2 py-1 rounded hover:bg-[var(--g-accent-dim)] transition-colors"
          >
            <span className="text-9px font-mono uppercase" style={{ color: "var(--g-text-muted)", letterSpacing: "0.12em" }}>
              Admin
            </span>
            <ChevronUp
              size={11}
              className="shrink-0 transition-transform duration-150"
              style={{ color: "var(--g-text-muted)", transform: adminOpen ? "rotate(180deg)" : "rotate(0deg)" }}
            />
          </button>
          {adminOpen && (
            <div className="space-y-0.5 mt-0.5">
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
            </div>
          )}
        </div>
      )}

      {/* Footer — user card + inline menu */}
      <div
        ref={menuRef}
        className="border-t shrink-0"
        style={{ borderColor: "var(--g-border)" }}
      >
        {/* Menu items — slide in above the trigger */}
        {menuOpen && (
          <div
            className="border-b overflow-hidden"
            style={{ borderColor: "var(--g-border)", background: "var(--g-surface)" }}
          >
            <Link
              href={`/profile/${user?.username}`}
              onClick={() => setMenuOpen(false)}
              className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-[var(--g-accent-dim)] transition-colors"
              style={{ color: "var(--g-text-muted)" }}
            >
              <User size={13} />
              My Profile
            </Link>
            <Link
              href="/settings"
              onClick={() => setMenuOpen(false)}
              className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-[var(--g-accent-dim)] transition-colors"
              style={{ color: "var(--g-text-muted)" }}
            >
              <Settings size={13} />
              Settings
            </Link>
            <div style={{ borderTop: "1px solid var(--g-border)" }} />
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-[var(--g-accent-dim)] transition-colors"
              style={{ color: "var(--g-danger, #f85149)" }}
            >
              <LogOut size={13} />
              Log Out
            </button>
          </div>
        )}

        {/* Trigger */}
        <button
          onClick={() => setMenuOpen((o) => !o)}
          className="w-full flex items-center gap-2 px-3 py-2 hover:bg-[var(--g-accent-dim)] transition-colors text-left"
        >
          <div className="flex-1 min-w-0">
            <div className="text-11 font-mono truncate" style={{ color: "var(--g-text)" }}>
              {user?.username ?? "—"}
            </div>
            <div className="flex items-center gap-1.5 mt-0.5">
              <Zap size={10} style={{ color: "var(--g-accent)", flexShrink: 0 }} />
              <span className="text-9px font-mono" style={{ color: "var(--g-accent)" }}>
                {profile?.total_points?.toLocaleString() ?? "0"} pts
              </span>
              {profile?.solve_count !== undefined && (
                <span className="text-9px font-mono" style={{ color: "var(--g-text-muted)" }}>
                  · {profile.solve_count} solve{profile.solve_count !== 1 ? "s" : ""}
                </span>
              )}
            </div>
            {myRank?.rank && (
              <div className="flex items-center gap-1 mt-0.5">
                <span
                  className="text-9px font-mono font-semibold"
                  style={{ color: myRank.rank.color ?? "var(--g-text-muted)" }}
                >
                  {myRank.rank.name}
                </span>
              </div>
            )}
          </div>
          <ChevronUp
            size={12}
            className="shrink-0 transition-transform duration-150"
            style={{
              color: "var(--g-text-muted)",
              transform: menuOpen ? "rotate(180deg)" : "rotate(0deg)",
            }}
          />
        </button>
      </div>
    </aside>
  );
}
