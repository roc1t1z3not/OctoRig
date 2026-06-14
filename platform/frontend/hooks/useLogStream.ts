"use client";

import { useEffect, useRef, useState } from "react";
import { useUserStore } from "@/stores/user.store";

interface Options {
  deploymentId: number;
  container?: string;
  tail?: number;
  enabled?: boolean;
}

export function useLogStream({ deploymentId, container = "app", tail = 100, enabled = true }: Options) {
  const [lines, setLines] = useState<string[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const { accessToken } = useUserStore();

  useEffect(() => {
    if (!enabled || !accessToken) return;

    const wsBase = process.env.NEXT_PUBLIC_API_URL?.replace(/^http/, "ws") ?? "";
    const url = `${wsBase}/api/v1/deployments/${deploymentId}/logs?container=${container}&tail=${tail}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ token: accessToken }));
      setConnected(true);
    };
    ws.onmessage = (e) => {
      const chunk: string = e.data;
      const newLines = chunk.split(/\r?\n/);
      setLines((prev) => {
        const next = [...prev, ...newLines].filter(Boolean);
        return next.slice(-2000); // keep last 2000 lines to avoid memory growth
      });
    };
    ws.onerror = () => setConnected(false);
    ws.onclose = () => setConnected(false);

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [deploymentId, container, tail, enabled, accessToken]);

  function clearLines() {
    setLines([]);
  }

  return { lines, connected, clearLines };
}
