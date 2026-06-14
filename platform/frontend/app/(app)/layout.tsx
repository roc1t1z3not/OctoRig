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
  const { accessToken, _hasHydrated } = useUserStore();
  const { theme } = useThemeStore();
  const router = useRouter();

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  useEffect(() => {
    if (_hasHydrated && !accessToken) router.replace("/login");
  }, [_hasHydrated, accessToken, router]);

  // Wait for Zustand to rehydrate from localStorage before rendering or redirecting.
  // Without this guard, accessToken starts as null for one tick even when the user
  // is logged in, causing unauthenticated API calls → 401 → redirect loop.
  if (!_hasHydrated || !accessToken) return null;

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
