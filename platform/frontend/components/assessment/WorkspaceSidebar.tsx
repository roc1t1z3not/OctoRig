"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { clsx } from "clsx";
import { Server, LayoutDashboard, FileText } from "lucide-react";

export const SECTIONS = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "labs", label: "Labs", icon: Server },
  { id: "report", label: "Report", icon: FileText },
] as const;

export type SectionId = (typeof SECTIONS)[number]["id"];

export function WorkspaceSidebar({ active, onSelect }: { active: SectionId; onSelect: (id: SectionId) => void }) {
  return (
    <aside
      className="w-44 shrink-0 flex flex-col"
      style={{ borderRight: "1px solid var(--g-border)", background: "var(--g-chrome)" }}
    >
      <nav className="p-2 space-y-0.5">
        {SECTIONS.map(({ id, label, icon: Icon }) => {
          const isActive = active === id;
          return (
            <button
              key={id}
              onClick={() => onSelect(id)}
              className={clsx("g-nav-item w-full text-left", isActive && "active")}
              style={isActive ? {
                background: "var(--g-accent-dim)",
                color: "var(--g-text)",
                borderColor: "var(--g-border-hover)",
              } : undefined}
            >
              <Icon
                size={14}
                className="shrink-0"
                style={{ color: isActive ? "var(--g-accent)" : "var(--g-text-muted)" }}
              />
              <span style={{ color: isActive ? "var(--g-text)" : "var(--g-text-muted)" }}>
                {label}
              </span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
