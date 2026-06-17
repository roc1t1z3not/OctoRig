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
      <main style={{ minHeight: "100vh", overflowY: "auto" }}>
        {children}
      </main>
      <Notifications />
      <ConfirmModal />
    </>
  );
}
