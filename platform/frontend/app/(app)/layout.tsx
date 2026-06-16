"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Construction, X } from "lucide-react";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { Notifications } from "@/components/ui/Notifications";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { useUserStore } from "@/stores/user.store";
import { useThemeStore } from "@/stores/theme.store";
import { getPublicSettings } from "@/lib/api/settings";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { accessToken, _hasHydrated, isRestoringToken, user } = useUserStore();
  const { theme } = useThemeStore();
  const router = useRouter();
  const [bannerDismissed, setBannerDismissed] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    if (_hasHydrated && !isRestoringToken && !accessToken) router.replace("/login");
  }, [_hasHydrated, isRestoringToken, accessToken, router]);

  const { data: publicSettings } = useQuery({
    queryKey: ["public-settings"],
    queryFn: getPublicSettings,
    staleTime: 300_000,
    enabled: !!accessToken,
  });

  // Wait for rehydration and any in-flight token restore before rendering or redirecting.
  if (!_hasHydrated || isRestoringToken || !accessToken) return null;

  const isAdmin = user?.is_admin || user?.is_superuser;
  const inMaintenance = publicSettings?.maintenance_mode ?? false;

  // Non-admins see a full maintenance screen
  if (inMaintenance && !isAdmin) {
    return (
      <div style={{
        display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
        minHeight: "100vh", gap: "1rem", padding: "2rem",
        background: "var(--g-chrome)", color: "var(--g-text)",
      }}>
        <Construction size={48} style={{ color: "var(--g-warning)" }} />
        <h1 style={{ fontSize: "1.5rem", fontWeight: 700, margin: 0 }}>Under Maintenance</h1>
        <p style={{ color: "var(--g-text-muted)", textAlign: "center", maxWidth: 400, margin: 0 }}>
          {publicSettings?.maintenance_message || "OctoRig is temporarily unavailable. Please check back soon."}
        </p>
      </div>
    );
  }

  return (
    <>
      {/* Maintenance banner for admins */}
      {inMaintenance && isAdmin && !bannerDismissed && (
        <div style={{
          display: "flex", alignItems: "center", justifyContent: "center", gap: "0.75rem",
          padding: "0.5rem 1rem",
          background: "color-mix(in srgb, var(--g-warning) 20%, transparent)",
          borderBottom: "1px solid color-mix(in srgb, var(--g-warning) 40%, transparent)",
          fontSize: "0.8125rem", color: "var(--g-warning)", position: "relative",
        }}>
          <Construction size={14} />
          <span>Maintenance mode is <strong>on</strong> — non-admin users see a maintenance screen.</span>
          <button
            onClick={() => setBannerDismissed(true)}
            style={{ position: "absolute", right: "1rem", background: "none", border: "none", cursor: "pointer", color: "inherit", padding: 0 }}
          >
            <X size={14} />
          </button>
        </div>
      )}
      <TopBar />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
      <Notifications />
      <ConfirmModal />
    </>
  );
}
