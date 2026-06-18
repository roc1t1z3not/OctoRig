"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useUserStore } from "@/stores/user.store";

export function useAdminGuard() {
  const { user } = useUserStore();
  const router = useRouter();
  useEffect(() => {
    if (user && !user.permissions?.includes("admin.panel")) router.replace("/");
  }, [user, router]);
}
