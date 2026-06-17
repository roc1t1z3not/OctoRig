// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
"use client";

import { useEffect } from "react";
import { useThemeStore } from "@/stores/theme.store";
import { Notifications } from "@/components/ui/Notifications";
import { ConfirmModal } from "@/components/ui/ConfirmModal";

export default function AssessmentLayout({ children }: { children: React.ReactNode }) {
  const { theme } = useThemeStore();

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  return (
    <>
      <main style={{ minHeight: "calc(100vh - 36px)", overflowY: "auto" }}>
        {children}
      </main>
      <footer
        style={{
          height: 36,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderTop: "1px solid var(--g-border)",
          background: "var(--g-chrome)",
        }}
      >
        <a
          href="https://github.com/CommonHuman-Lab"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            fontSize: "0.625rem",
            fontFamily: "var(--font-mono, monospace)",
            letterSpacing: "0.06em",
            color: "var(--g-text-muted)",
            textDecoration: "none",
            opacity: 0.6,
          }}
        >
          By CommonHuman
        </a>
      </footer>
      <Notifications />
      <ConfirmModal />
    </>
  );
}
