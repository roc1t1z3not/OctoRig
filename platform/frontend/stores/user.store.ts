"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  is_candidate: boolean;
  platform_roles?: string[];
  permissions?: string[];
}

interface UserState {
  user: AuthUser | null;
  accessToken: string | null;
  _hasHydrated: boolean;
  isRestoringToken: boolean;

  setSession: (user: AuthUser, accessToken: string) => void;
  clearSession: () => void;
  setAccessToken: (token: string) => void;
  setHasHydrated: (v: boolean) => void;
  setIsRestoringToken: (v: boolean) => void;
}

export const useUserStore = create<UserState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      _hasHydrated: false,
      isRestoringToken: false,

      setSession: (user, accessToken) => set({ user, accessToken }),
      clearSession: () => set({ user: null, accessToken: null }),
      setAccessToken: (accessToken) => set({ accessToken }),
      setHasHydrated: (v) => set({ _hasHydrated: v }),
      setIsRestoringToken: (v) => set({ isRestoringToken: v }),
    }),
    {
      name: "octorig_user",
      // Access token is NOT persisted — lives in memory only.
      partialize: (state) => ({ user: state.user }),
      onRehydrateStorage: () => (state) => {
        state?.setHasHydrated(true);
        if (state?.user) {
          state.setIsRestoringToken(true);
        }
      },
    }
  )
);
