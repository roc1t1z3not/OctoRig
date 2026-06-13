"use client";

import { create } from "zustand";

export type NotificationKind = "success" | "error" | "warning" | "info";

export interface Notification {
  id: string;
  kind: NotificationKind;
  message: string;
}

interface NotificationsState {
  items: Notification[];
  push: (kind: NotificationKind, message: string) => void;
  dismiss: (id: string) => void;
}

export const useNotificationsStore = create<NotificationsState>((set) => ({
  items: [],
  push: (kind, message) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    set((s) => ({ items: [...s.items, { id, kind, message }] }));
    setTimeout(() => set((s) => ({ items: s.items.filter((n) => n.id !== id) })), 5000);
  },
  dismiss: (id) => set((s) => ({ items: s.items.filter((n) => n.id !== id) })),
}));
