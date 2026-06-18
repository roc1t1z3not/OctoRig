"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { wsClient } from "@/lib/ws";
import { useLiveStore } from "@/stores/live.store";
import { useUserStore } from "@/stores/user.store";
import type { OctoEvent } from "@/lib/ws";
import type { LiveDeployment, LiveHealth } from "@/stores/live.store";

export function WSProvider({ children }: { children: React.ReactNode }) {
  const qc = useQueryClient();
  const accessToken = useUserStore((s) => s.accessToken);

  useEffect(() => {
    if (!accessToken) return;
    wsClient.connect(() => useUserStore.getState().accessToken);

    const live = () => useLiveStore.getState();

    const unsubs = [
      wsClient.onStateChange((state) => {
        live().setConnected(state === "connected");
      }),

      wsClient.on("deployment.update", (e: OctoEvent) => {
        live().upsertDeployment(e.data as LiveDeployment);
        qc.invalidateQueries({ queryKey: ["deployments"] });
        qc.invalidateQueries({ queryKey: ["labs"] });
        qc.invalidateQueries({ queryKey: ["system-health"] });
      }),

      wsClient.on("health.update", (e: OctoEvent) => {
        live().setHealth(e.data as LiveHealth);
        qc.invalidateQueries({ queryKey: ["system-health"] });
      }),

      wsClient.on("notification.new", () => {
        qc.invalidateQueries({ queryKey: ["notifications"] });
        qc.invalidateQueries({ queryKey: ["notifications-unread"] });
      }),
    ];

    return () => {
      unsubs.forEach((fn) => fn());
      wsClient.disconnect();
    };
  }, [qc, accessToken]);

  return <>{children}</>;
}
