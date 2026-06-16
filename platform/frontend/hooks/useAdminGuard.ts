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
    if (user && !user.is_admin && !user.is_superuser) router.replace("/");
  }, [user, router]);
}
