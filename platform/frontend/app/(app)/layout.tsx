"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { Notifications } from "@/components/ui/Notifications";
import { ConfirmModal } from "@/components/ui/ConfirmModal";
import { useUserStore } from "@/stores/user.store";
import { useThemeStore } from "@/stores/theme.store";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { accessToken, _hasHydrated, isRestoringToken } = useUserStore();
  const { theme } = useThemeStore();
  const router = useRouter();

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    if (_hasHydrated && !isRestoringToken && !accessToken) router.replace("/login");
  }, [_hasHydrated, isRestoringToken, accessToken, router]);

  // Wait for rehydration and any in-flight token restore before rendering or redirecting.
  if (!_hasHydrated || isRestoringToken || !accessToken) return null;

  return (
    <>
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
