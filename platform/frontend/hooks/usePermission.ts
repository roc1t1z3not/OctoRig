"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useUserStore } from "@/stores/user.store";

export function usePermission(perm: string): boolean {
  const user = useUserStore((s) => s.user);
  return user?.permissions?.includes(perm) ?? false;
}
