"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { create } from "zustand";

export interface ConfirmOptions {
  title: string;
  body?: string;
  confirmLabel?: string;
  dangerous?: boolean;
  onConfirm: () => void;
}

interface ConfirmState {
  pending: ConfirmOptions | null;
  confirm: (opts: ConfirmOptions) => void;
  resolve: (confirmed: boolean) => void;
}

export const useConfirmStore = create<ConfirmState>((set, get) => ({
  pending: null,
  confirm: (opts) => set({ pending: opts }),
  resolve: (confirmed) => {
    const { pending } = get();
    if (confirmed && pending) pending.onConfirm();
    set({ pending: null });
  },
}));
