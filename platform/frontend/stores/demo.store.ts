"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface DemoState {
  isDemoMode: boolean;
  toggle: () => void;
}

export const useDemoStore = create<DemoState>()(
  persist(
    (set, get) => ({
      isDemoMode: false,
      toggle: () => set({ isDemoMode: !get().isDemoMode }),
    }),
    { name: "octorig_demo" }
  )
);

export const isDemoMode = () => useDemoStore.getState().isDemoMode;
