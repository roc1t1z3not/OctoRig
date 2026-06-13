"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { type ThemeId, THEME_STORAGE_KEY } from "@/lib/themes";

interface ThemeState {
  theme: ThemeId;
  setTheme: (t: ThemeId) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: "nightfall",
      setTheme: (theme) => {
        if (typeof document !== "undefined") {
          document.documentElement.setAttribute("data-theme", theme);
        }
        set({ theme });
      },
    }),
    { name: THEME_STORAGE_KEY }
  )
);
