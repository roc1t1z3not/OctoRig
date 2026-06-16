// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import type { EventStatus } from "@/lib/api/events";

export const EVENT_STATUS_COLORS: Record<EventStatus, string> = {
  draft: "var(--g-text-muted)",
  published: "var(--g-accent)",
  running: "var(--g-success)",
  ended: "var(--g-text-muted)",
  archived: "var(--g-text-muted)",
};
