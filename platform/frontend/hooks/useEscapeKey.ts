// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect } from "react";

export function useEscapeKey(onEscape: () => void, active: boolean) {
  useEffect(() => {
    if (!active) return;
    function handler(e: KeyboardEvent) {
      if (e.key === "Escape") onEscape();
    }
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [active, onEscape]);
}
