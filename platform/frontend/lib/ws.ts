"use client";

export type WsState = "connecting" | "connected" | "disconnected";

export interface OctoEvent {
  type: string;
  data: unknown;
}

type Handler = (e: OctoEvent) => void;

class OctoWSClient {
  private ws: WebSocket | null = null;
  private handlers = new Map<string, Set<Handler>>();
  private stateHandlers = new Set<(s: WsState) => void>();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnectCount = 0;
  private reconnectDelay = 2_000;
  private readonly url: string;
  state: WsState = "disconnected";

  constructor(url: string) {
    this.url = url;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    this._setState("connecting");
    const ws = new WebSocket(this.url);
    this.ws = ws;

    ws.onopen = () => {
      this.reconnectCount = 0;
      this.reconnectDelay = 2_000;
      this._setState("connected");
    };

    ws.onmessage = (e: MessageEvent) => {
      try {
        const event: OctoEvent = JSON.parse(e.data as string);
        if (!event.type || event.type === "pong") return;
        this._dispatch(event.type, event);
        this._dispatch("*", event);
      } catch {
        // ignore malformed frames
      }
    };

    ws.onclose = () => {
      this._setState("disconnected");
      this.reconnectCount++;
      this.reconnectDelay = Math.min(this.reconnectDelay * 1.5, 30_000);
      this.reconnectTimer = setTimeout(() => this.connect(), this.reconnectDelay);
    };

    ws.onerror = () => ws.close();
  }

  disconnect(): void {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.reconnectTimer = null;
    this.ws?.close();
    this._setState("disconnected");
  }

  /** Subscribe to a specific event type (or "*" for all). Returns unsubscribe fn. */
  on(type: string, handler: Handler): () => void {
    if (!this.handlers.has(type)) this.handlers.set(type, new Set());
    this.handlers.get(type)!.add(handler);
    return () => this.handlers.get(type)?.delete(handler);
  }

  onStateChange(handler: (s: WsState) => void): () => void {
    this.stateHandlers.add(handler);
    return () => this.stateHandlers.delete(handler);
  }

  private _dispatch(type: string, event: OctoEvent): void {
    this.handlers.get(type)?.forEach((h) => {
      try { h(event); } catch { /* ignore */ }
    });
  }

  private _setState(s: WsState): void {
    this.state = s;
    this.stateHandlers.forEach((h) => {
      try { h(s); } catch { /* ignore */ }
    });
  }
}

const WS_URL =
  typeof window !== "undefined"
    ? (process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws/events")
    : "ws://localhost:8000/ws/events";

export const wsClient = new OctoWSClient(WS_URL);
